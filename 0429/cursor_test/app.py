"""
基于 Dash + Plotly + pandas 的数据探索 Web 应用。

运行方式::
    python app.py

启动后会在默认浏览器中打开 http://127.0.0.1:8050
"""

from __future__ import annotations

import threading
import webbrowser

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, callback, dcc, dash_table, html, no_update
from dash.exceptions import PreventUpdate
from scipy.stats import gaussian_kde

import analytics as an
from session_store import decode_upload, load_dataframe, sessions

# -----------------------------------------------------------------------------
# Dash 应用与样式
# -----------------------------------------------------------------------------
external_stylesheets = [dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME]
app = Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
)
app.title = "数据探索工作台"

PLOT_SAMPLE = 40_000

TAB_VALUES = {
    "overview": "概览",
    "missing": "缺失值",
    "describe": "描述统计",
    "corr": "相关性",
    "num_dist": "数值分布",
    "cat_dist": "分类分布",
    "groupby": "分组统计",
    "pivot": "透视表",
}


def _empty_fig(msg: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=msg,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=14),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def _no_session_alert() -> dbc.Alert:
    return dbc.Alert("请先上传数据文件。", color="info", className="mt-2")


def dash_dt(rows: list, columns: list | None = None) -> dash_table.DataTable:
    """构建 DataTable。"""
    if columns is None and rows:
        columns = [{"name": k, "id": k} for k in rows[0].keys()]
    elif columns is None:
        columns = []
    return dash_table.DataTable(
        columns=columns,
        data=rows,
        page_size=15,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "minWidth": "80px"},
        style_header={"fontWeight": "bold"},
    )


def _categorical_columns(df: pd.DataFrame) -> list[str]:
    """启发式选取分类型列。"""
    out: list[str] = []
    for c in df.columns:
        if (
            df[c].dtype == object
            or pd.api.types.is_categorical_dtype(df[c])
            or str(df[c].dtype) == "string"
        ):
            out.append(c)
    for c in df.columns:
        if c in out:
            continue
        if not pd.api.types.is_numeric_dtype(df[c]):
            out.append(c)
    return out


def build_layout() -> dbc.Container:
    """构建响应式主布局；所有交互控件常驻 DOM，避免回调引用未挂载组件。"""
    tabs_children = [
        dbc.Tab(
            tab_id="overview",
            label=TAB_VALUES["overview"],
            children=dbc.Card(
                dbc.CardBody(html.Div(id="overview-panel")),
                className="shadow-sm mt-2",
            ),
        ),
        dbc.Tab(
            tab_id="missing",
            label=TAB_VALUES["missing"],
            children=dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("各列缺失情况"),
                        html.Div(id="missing-table-wrap"),
                        dbc.Spinner(
                            dcc.Graph(id="missing-chart", figure=_empty_fig("加载中…")),
                            color="primary",
                        ),
                    ]
                ),
                className="shadow-sm mt-2",
            ),
        ),
        dbc.Tab(
            tab_id="describe",
            label=TAB_VALUES["describe"],
            children=dbc.Card(
                dbc.CardBody(html.Div(id="describe-panel")),
                className="shadow-sm mt-2",
            ),
        ),
        dbc.Tab(
            tab_id="corr",
            label=TAB_VALUES["corr"],
            children=dbc.Card(
                dbc.CardBody(
                    [
                        html.Label("相关系数方法"),
                        dcc.RadioItems(
                            id="corr-method",
                            options=[
                                {"label": " Pearson ", "value": "pearson"},
                                {"label": " Spearman ", "value": "spearman"},
                            ],
                            value="pearson",
                            inline=True,
                            className="mb-2",
                        ),
                        dbc.Spinner(
                            dcc.Graph(id="corr-heatmap", figure=_empty_fig("请选择数据")),
                            color="primary",
                        ),
                    ]
                ),
                className="shadow-sm mt-2",
            ),
        ),
        dbc.Tab(
            tab_id="num_dist",
            label=TAB_VALUES["num_dist"],
            children=dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Label("选择数值列"),
                                        dcc.Dropdown(
                                            id="num-col",
                                            options=[],
                                            clearable=False,
                                        ),
                                    ],
                                    xs=12,
                                    md=4,
                                ),
                                dbc.Col(
                                    [
                                        html.Label("直方图 bins 数量"),
                                        dcc.Slider(
                                            id="num-bins",
                                            min=10,
                                            max=100,
                                            step=5,
                                            value=30,
                                            marks=None,
                                            tooltip={
                                                "placement": "bottom",
                                                "always_visible": True,
                                            },
                                        ),
                                    ],
                                    xs=12,
                                    md=4,
                                ),
                                dbc.Col(
                                    [
                                        html.Label("显示范围（数值轴）"),
                                        dcc.RangeSlider(
                                            id="num-range",
                                            min=0,
                                            max=1,
                                            step=0.0001,
                                            value=[0, 1],
                                            allowCross=False,
                                        ),
                                    ],
                                    xs=12,
                                    md=4,
                                ),
                            ],
                            className="g-2 mb-2",
                        ),
                        dbc.Spinner(
                            dcc.Graph(id="num-dist-graph", figure=_empty_fig("请选择数据")),
                            color="primary",
                        ),
                    ]
                ),
                className="shadow-sm mt-2",
            ),
        ),
        dbc.Tab(
            tab_id="cat_dist",
            label=TAB_VALUES["cat_dist"],
            children=dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            dbc.Col(
                                [
                                    html.Label("选择分类型列"),
                                    dcc.Dropdown(
                                        id="cat-col",
                                        options=[],
                                        clearable=False,
                                    ),
                                ],
                                width=12,
                                md=6,
                            ),
                            className="mb-2",
                        ),
                        html.H6("频数表"),
                        html.Div(id="cat-table-wrap"),
                        dbc.Spinner(
                            dcc.Graph(id="cat-bar-graph", figure=_empty_fig("请选择数据")),
                            color="primary",
                        ),
                    ]
                ),
                className="shadow-sm mt-2",
            ),
        ),
        dbc.Tab(
            tab_id="groupby",
            label=TAB_VALUES["groupby"],
            children=dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Label("分组列（可多选）"),
                                        dcc.Dropdown(
                                            id="gb-cols",
                                            options=[],
                                            multi=True,
                                            placeholder="选择一列或多列",
                                        ),
                                    ],
                                    xs=12,
                                    md=4,
                                ),
                                dbc.Col(
                                    [
                                        html.Label("聚合列"),
                                        dcc.Dropdown(id="gb-agg-col", options=[], clearable=False),
                                    ],
                                    xs=12,
                                    md=4,
                                ),
                                dbc.Col(
                                    [
                                        html.Label("聚合函数"),
                                        dcc.Dropdown(
                                            id="gb-func",
                                            options=[
                                                {"label": "求和 sum", "value": "sum"},
                                                {"label": "均值 mean", "value": "mean"},
                                                {
                                                    "label": "中位数 median",
                                                    "value": "median",
                                                },
                                                {"label": "最小 min", "value": "min"},
                                                {"label": "最大 max", "value": "max"},
                                                {"label": "计数 count", "value": "count"},
                                                {"label": "标准差 std", "value": "std"},
                                                {
                                                    "label": "唯一值数 nunique",
                                                    "value": "nunique",
                                                },
                                            ],
                                            value="mean",
                                            clearable=False,
                                        ),
                                    ],
                                    xs=12,
                                    md=4,
                                ),
                            ],
                            className="g-2",
                        ),
                        dbc.Button("执行分组统计", id="gb-run", color="primary", className="my-2"),
                        html.Div(id="gb-result"),
                    ]
                ),
                className="shadow-sm mt-2",
            ),
        ),
        dbc.Tab(
            tab_id="pivot",
            label=TAB_VALUES["pivot"],
            children=dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Alert(
                            "行索引与列字段至少填写一个；值为要聚合的字段。",
                            color="info",
                            className="py-2",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Label("行 (index)"),
                                        dcc.Dropdown(
                                            id="pv-index",
                                            options=[],
                                            clearable=True,
                                            placeholder="可选",
                                        ),
                                    ],
                                    xs=12,
                                    md=3,
                                ),
                                dbc.Col(
                                    [
                                        html.Label("列 (columns)"),
                                        dcc.Dropdown(
                                            id="pv-columns",
                                            options=[],
                                            clearable=True,
                                            placeholder="可选",
                                        ),
                                    ],
                                    xs=12,
                                    md=3,
                                ),
                                dbc.Col(
                                    [
                                        html.Label("值 (values)"),
                                        dcc.Dropdown(id="pv-values", options=[], clearable=False),
                                    ],
                                    xs=12,
                                    md=3,
                                ),
                                dbc.Col(
                                    [
                                        html.Label("聚合函数"),
                                        dcc.Dropdown(
                                            id="pv-agg",
                                            options=[
                                                {"label": "mean", "value": "mean"},
                                                {"label": "sum", "value": "sum"},
                                                {"label": "count", "value": "count"},
                                                {"label": "min", "value": "min"},
                                                {"label": "max", "value": "max"},
                                                {"label": "median", "value": "median"},
                                            ],
                                            value="mean",
                                            clearable=False,
                                        ),
                                    ],
                                    xs=12,
                                    md=3,
                                ),
                            ],
                            className="g-2",
                        ),
                        dbc.Button("生成透视表", id="pv-run", color="primary", className="my-2"),
                        html.Div(id="pv-result"),
                    ]
                ),
                className="shadow-sm mt-2",
            ),
        ),
    ]

    return dbc.Container(
        [
            dcc.Store(id="session-store", data=None),
            dbc.Row(
                dbc.Col(
                    [
                        html.H1(
                            [html.I(className="fas fa-chart-line me-2"), "数据探索工作台"],
                            className="my-3 text-center",
                        ),
                        html.P(
                            "上传 CSV / Excel，切换页签进行分析；图表在后台抽样以保障流畅。",
                            className="text-muted text-center lead small",
                        ),
                    ],
                    width=12,
                )
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Upload(
                                id="upload-data",
                                children=html.Div(
                                    [
                                        html.I(
                                            className="fas fa-cloud-upload-alt fa-2x mb-2 text-primary"
                                        ),
                                        html.Div(
                                            [
                                                html.Strong("拖放文件到此处"),
                                                " 或 ",
                                                html.A("点击选择文件", className="text-primary"),
                                            ]
                                        ),
                                        html.Small(
                                            "支持 .csv、.xlsx、.xls",
                                            className="text-muted",
                                        ),
                                    ],
                                    className="text-center py-4",
                                ),
                                style={
                                    "width": "100%",
                                    "borderWidth": "2px",
                                    "borderStyle": "dashed",
                                    "borderRadius": "8px",
                                    "borderColor": "#0d6efd",
                                    "cursor": "pointer",
                                    "backgroundColor": "#f8f9fa",
                                },
                                multiple=False,
                            ),
                            html.Div(id="upload-status", className="mt-2"),
                            dbc.Spinner(html.Div(id="upload-loading"), color="primary"),
                        ],
                        xs=12,
                        md=10,
                        lg=8,
                        className="mx-auto",
                    )
                ],
                className="mb-3",
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Tabs(
                        id="main-tabs",
                        active_tab="overview",
                        children=tabs_children,
                        className="mb-3",
                        persistence=True,
                        persistence_type="session",
                    ),
                    width=12,
                )
            ),
        ],
        fluid=True,
        className="py-2 px-3",
    )


app.layout = build_layout


def _df_from_store(store: dict | None) -> pd.DataFrame | None:
    if not store or not store.get("session_id"):
        return None
    return sessions.get(store["session_id"])


@callback(
    Output("session-store", "data"),
    Output("upload-status", "children"),
    Output("upload-loading", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True,
)
def on_upload(contents: str | None, filename: str | None):
    """解析上传文件并写入服务端会话。"""
    if not contents or not filename:
        raise PreventUpdate
    try:
        raw = decode_upload(contents)
        size_mb = round(len(raw) / (1024**2), 4)
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        df, info = load_dataframe(filename, raw)
        meta = {
            "filename": filename,
            "size_mb": size_mb,
            "format": ext,
            "truncated": info["truncated"],
            "original_rows": info["original_rows"],
        }
        sid = sessions.put(df, meta)
        warn = []
        if info["truncated"]:
            warn.append(
                dbc.Alert(
                    f"数据行数超过上限，已仅保留前 {info['stored_rows']:,} 行用于分析。",
                    color="warning",
                    className="mt-2 py-2",
                )
            )
        status = dbc.Alert(
            [
                html.Strong("上传成功："),
                f"{filename} | 大小 {size_mb} MB | 格式 {ext} | 行数 {len(df):,} × 列数 {len(df.columns)}",
            ],
            color="success",
            className="mb-0",
        )
        store = {"session_id": sid, **meta}
        return store, html.Div([status, *warn]), ""
    except Exception as e:  # noqa: BLE001
        err = dbc.Alert(f"处理文件失败：{e}", color="danger", className="mb-0")
        return no_update, err, ""


@callback(
    Output("num-col", "options"),
    Output("num-col", "value"),
    Output("cat-col", "options"),
    Output("cat-col", "value"),
    Output("gb-cols", "options"),
    Output("gb-agg-col", "options"),
    Output("gb-agg-col", "value"),
    Output("pv-index", "options"),
    Output("pv-columns", "options"),
    Output("pv-values", "options"),
    Output("pv-values", "value"),
    Input("session-store", "data"),
)
def sync_dropdowns(store: dict | None):
    """上传后一次性填充各页签下拉选项（懒加载数据，仅更新控件元数据）。"""
    df = _df_from_store(store)
    if df is None:
        empty = []
        return (empty, None, empty, None, empty, empty, None, empty, empty, empty, None)
    col_opts = [{"label": c, "value": c} for c in df.columns]
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    num_opts = [{"label": c, "value": c} for c in num_cols]
    num_val = num_cols[0] if num_cols else None
    cat_cols = _categorical_columns(df)
    cat_opts = [{"label": c, "value": c} for c in cat_cols]
    cat_val = cat_cols[0] if cat_cols else None
    agg_candidates = num_cols if num_cols else list(df.columns)
    gb_agg_val = agg_candidates[0] if agg_candidates else None
    pv_val = df.columns[0] if len(df.columns) else None
    return (
        num_opts,
        num_val,
        cat_opts,
        cat_val,
        col_opts,
        col_opts,
        gb_agg_val,
        col_opts,
        col_opts,
        col_opts,
        pv_val,
    )


@callback(Output("overview-panel", "children"), Input("session-store", "data"))
def update_overview(store: dict | None):
    """数据概览。"""
    df = _df_from_store(store)
    if df is None:
        return _no_session_alert()
    sessions.touch(store["session_id"])
    ov = an.basic_overview(df)
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H6("总行数", className="text-muted"),
                                    html.H3(f"{ov['n_rows']:,}", className="mb-0"),
                                ]
                            ),
                            className="shadow-sm mb-3",
                        ),
                        xs=6,
                        md=3,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H6("总列数", className="text-muted"),
                                    html.H3(f"{ov['n_cols']}", className="mb-0"),
                                ]
                            ),
                            className="shadow-sm mb-3",
                        ),
                        xs=6,
                        md=3,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H6("内存占用 (MB)", className="text-muted"),
                                    html.H3(f"{ov['memory_mb']}", className="mb-0"),
                                ]
                            ),
                            className="shadow-sm mb-3",
                        ),
                        xs=6,
                        md=3,
                    ),
                ],
                className="g-2",
            ),
            html.H5("列类型", className="mt-2"),
            dbc.Spinner(dash_dt(ov["types"]), color="primary"),
            html.H5("前 10 行预览", className="mt-3"),
            dbc.Spinner(
                dash_dt(ov["preview_data"], ov["preview_columns"]),
                color="primary",
            ),
        ]
    )


def _missing_figure(rows: list) -> go.Figure:
    if not rows:
        return _empty_fig("无数据")
    cols = [r["列名"] for r in rows]
    vals = [r["缺失比例(%)"] for r in rows]
    fig = go.Figure(
        go.Bar(
            x=cols,
            y=vals,
            marker_color="#0d6efd",
            hovertemplate="列: %{x}<br>缺失比例: %{y:.2f}%<extra></extra>",
        )
    )
    fig.update_layout(
        title="缺失比例 (%)",
        xaxis_title="列名",
        yaxis_title="缺失比例 %",
        margin=dict(l=40, r=20, t=50, b=120),
        xaxis_tickangle=-45,
        height=420,
        autosize=True,
    )
    return fig


@callback(
    Output("missing-table-wrap", "children"),
    Output("missing-chart", "figure"),
    Input("session-store", "data"),
    Input("main-tabs", "active_tab"),
)
def update_missing(store: dict | None, active_tab: str | None):
    """缺失值分析：仅在「缺失值」页签激活时重绘图表，减轻负担。"""
    df = _df_from_store(store)
    if df is None:
        return _no_session_alert(), _empty_fig("请先上传数据")
    ma = an.missing_analysis(df)
    table = dbc.Spinner(dash_dt(ma["rows"]), color="primary")
    if active_tab != "missing":
        return table, no_update
    return table, _missing_figure(ma["rows"])


@callback(Output("describe-panel", "children"), Input("session-store", "data"))
def update_describe(store: dict | None):
    """数值描述统计。"""
    df = _df_from_store(store)
    if df is None:
        return _no_session_alert()
    desc = an.describe_numeric(df)
    if desc.empty:
        return dbc.Alert("当前数据没有数值型列。", color="secondary")
    records = desc.reset_index().rename(columns={"index": "特征"})
    records = records.replace({np.nan: None}).to_dict("records")
    cols = [{"name": c, "id": c} for c in records[0].keys()] if records else []
    return dbc.Spinner(
        dash_table.DataTable(
            columns=cols,
            data=records,
            page_size=12,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left"},
            style_header={"fontWeight": "bold"},
        ),
        color="primary",
    )


@callback(
    Output("corr-heatmap", "figure"),
    Input("session-store", "data"),
    Input("main-tabs", "active_tab"),
    Input("corr-method", "value"),
)
def update_corr_heatmap(store: dict | None, active_tab: str | None, method: str | None):
    """相关性热力图：仅在相关性页签时计算。"""
    if active_tab != "corr":
        raise PreventUpdate
    df = _df_from_store(store)
    if df is None:
        return _empty_fig("请先上传数据")
    corr, _ = an.correlation_matrix(df, method=method or "pearson")
    if corr.empty or corr.shape[0] < 2:
        return _empty_fig("至少需要两列数值型数据")
    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=list(corr.columns),
            y=list(corr.index),
            colorscale="RdBu",
            zmid=0,
            hoverongaps=False,
        )
    )
    fig.update_layout(
        title=f"相关性矩阵 ({method})",
        margin=dict(l=80, r=40, t=60, b=80),
        height=min(520, 80 + 18 * len(corr.columns)),
        autosize=True,
    )
    return fig


@callback(
    Output("num-range", "min"),
    Output("num-range", "max"),
    Output("num-range", "value"),
    Input("num-col", "value"),
    Input("session-store", "data"),
)
def sync_num_range(col: str | None, store: dict | None):
    """切换数值列时同步范围滑块。"""
    df = _df_from_store(store)
    if df is None or not col or col not in df.columns:
        return 0.0, 1.0, [0.0, 1.0]
    s = an.sample_for_plot(df[col], PLOT_SAMPLE)
    vmin, vmax = float(s.min()), float(s.max())
    if vmin == vmax:
        vmax = vmin + 1e-9
    return vmin, vmax, [vmin, vmax]


@callback(
    Output("num-dist-graph", "figure"),
    Input("session-store", "data"),
    Input("main-tabs", "active_tab"),
    Input("num-col", "value"),
    Input("num-bins", "value"),
    Input("num-range", "value"),
)
def update_num_dist(
    store: dict | None,
    active_tab: str | None,
    col: str | None,
    bins,
    value_range,
):
    """直方图 + KDE；仅在数值分布页签绘制。"""
    if active_tab != "num_dist":
        raise PreventUpdate
    df = _df_from_store(store)
    if df is None or not col or col not in df.columns:
        return _empty_fig("请先上传并选择数值列")
    s_full = df[col].dropna()
    if s_full.empty:
        return _empty_fig("该列无有效数值")
    s = an.sample_for_plot(s_full, PLOT_SAMPLE)
    smin, smax = float(s.min()), float(s.max())
    if smin == smax:
        smax = smin + 1e-9
    lo, hi = value_range if value_range else (smin, smax)
    s_clip = s[(s >= lo) & (s <= hi)]
    # RangeSlider 默认值可能在会话加载瞬间未同步，回退到抽样全范围
    if s_clip.empty:
        lo, hi = smin, smax
        s_clip = s[(s >= lo) & (s <= hi)]
    if s_clip.empty:
        return _empty_fig("所选范围内无数据点")
    nbins = int(bins) if bins else 30
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=s_clip,
            nbinsx=nbins,
            name="直方图",
            opacity=0.65,
            histnorm="probability density",
        )
    )
    if len(s_clip) >= 5:
        try:
            kde = gaussian_kde(s_clip.astype(float))
            xs = np.linspace(lo, hi, 200)
            ys = kde(xs)
            fig.add_trace(
                go.Scatter(
                    x=xs,
                    y=ys,
                    mode="lines",
                    name="KDE",
                    line=dict(width=2, color="#d63384"),
                )
            )
        except Exception:  # noqa: BLE001
            pass
    fig.update_layout(
        barmode="overlay",
        title=f"{col} 分布（抽样至多 {PLOT_SAMPLE:,} 点）",
        xaxis_title=col,
        yaxis_title="密度",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=50, r=20, t=60, b=50),
        height=440,
        autosize=True,
    )
    return fig


@callback(
    Output("cat-table-wrap", "children"),
    Output("cat-bar-graph", "figure"),
    Input("session-store", "data"),
    Input("main-tabs", "active_tab"),
    Input("cat-col", "value"),
)
def update_cat_dist(store: dict | None, active_tab: str | None, col: str | None):
    """分类频数表与条形图。"""
    df = _df_from_store(store)
    if df is None:
        return _no_session_alert(), _empty_fig("请先上传数据")
    if not col or col not in df.columns:
        return html.Div(), _empty_fig("请选择列")
    freq = an.categorical_frequency(df, col, top_n=40)
    records = freq.replace({np.nan: None}).to_dict("records")
    cols = [{"name": c, "id": c} for c in freq.columns]
    table = dash_dt(records, cols)
    if active_tab != "cat_dist":
        return table, no_update
    fig = go.Figure(
        go.Bar(
            x=freq["类别"].astype(str),
            y=freq["频数"],
            marker_color="#198754",
            hovertemplate="类别: %{x}<br>频数: %{y}<extra></extra>",
        )
    )
    fig.update_layout(
        title=f"{col} 频数分布（Top 40）",
        xaxis_title="类别",
        yaxis_title="频数",
        margin=dict(l=40, r=20, t=50, b=140),
        xaxis_tickangle=-45,
        height=420,
        autosize=True,
    )
    return html.Div([table]), fig


@callback(
    Output("gb-result", "children"),
    Input("gb-run", "n_clicks"),
    State("session-store", "data"),
    State("gb-cols", "value"),
    State("gb-agg-col", "value"),
    State("gb-func", "value"),
    prevent_initial_call=True,
)
def run_groupby_cb(n_clicks, store, group_cols, agg_col, agg_func):
    """分组统计。"""
    if not n_clicks or not store:
        raise PreventUpdate
    df = _df_from_store(store)
    if df is None:
        return dbc.Alert("会话无效", color="warning")
    try:
        out = an.run_groupby(df, list(group_cols or []), str(agg_col), str(agg_func))
    except Exception as e:  # noqa: BLE001
        return dbc.Alert(str(e), color="danger")
    records = out.replace({np.nan: None}).to_dict("records")
    columns = [{"name": c, "id": c} for c in out.columns]
    return dbc.Spinner(
        dash_table.DataTable(
            columns=columns,
            data=records,
            page_size=15,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left"},
        ),
        color="primary",
    )


@callback(
    Output("pv-result", "children"),
    Input("pv-run", "n_clicks"),
    State("session-store", "data"),
    State("pv-index", "value"),
    State("pv-columns", "value"),
    State("pv-values", "value"),
    State("pv-agg", "value"),
    prevent_initial_call=True,
)
def run_pivot_cb(n_clicks, store, index, columns, values, aggfunc):
    """透视表。"""
    if not n_clicks or not store:
        raise PreventUpdate
    df = _df_from_store(store)
    if df is None:
        return dbc.Alert("会话无效", color="warning")
    if not index and not columns:
        return dbc.Alert("请至少选择行或列之一。", color="warning")
    try:
        out = an.run_pivot(df, index, columns, str(values), str(aggfunc))
    except Exception as e:  # noqa: BLE001
        return dbc.Alert(str(e), color="danger")
    records = out.replace({np.nan: None}).to_dict("records")
    tbl_cols = [{"name": str(c), "id": str(c)} for c in out.columns]
    return dbc.Spinner(
        dash_table.DataTable(
            columns=tbl_cols,
            data=records,
            page_size=15,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left"},
        ),
        color="primary",
    )


def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")


if __name__ == "__main__":
    threading.Timer(1.2, open_browser).start()
    app.run(debug=False, use_reloader=False, host="127.0.0.1", port=8050)
