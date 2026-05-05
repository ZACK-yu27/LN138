"""
数据探索Web应用程序
基于Dash和Plotly构建的数据分析与可视化工具
"""

import base64
import io

import dash
from dash import dcc, html, dash_table, callback, Input, Output, State, no_update
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots


app = dash.Dash(
    __name__,
    title="数据探索应用",
    update_title="加载中..."
)

server = app.server

app.layout = html.Div([
    dcc.Store(id='stored-data', data=None),
    dcc.Store(id='file-info-store', data=None),
    
    html.Div([
        html.H1("数据探索应用", className="app-title"),
        html.P("基于Dash和Plotly构建的数据分析与可视化工具", className="app-subtitle")
    ], className="header"),
    
    html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                html.I(className="fas fa-cloud-upload-alt upload-icon"),
                html.P("拖拽文件到此处或点击选择"),
                html.P(".xlsx, .xls, .csv", className="upload-hint")
            ]),
            multiple=False,
            className="upload-container"
        ),
    ], className="upload-section"),
    
    html.Div(id='file-info-display', className="file-info"),
    
    html.Div(id='analysis-content', style={'display': 'none'}, children=[
        dcc.Tabs(id='analysis-tabs', value='overview', children=[
            dcc.Tab(label='数据概览', value='overview', children=[
                html.Div([
                    html.H2("数据基本概览", className="section-title"),
                    html.Div(id='overview-stats', className="stats-row"),
                    html.Div(id='overview-types-table'),
                    html.Div(id='overview-preview-table')
                ])
            ]),
            dcc.Tab(label='缺失值分析', value='missing', children=[
                html.Div([
                    html.H2("缺失值分析", className="section-title"),
                    html.Div(id='missing-table'),
                    html.Div([dcc.Graph(id='missing-chart')], className="chart-container")
                ])
            ]),
            dcc.Tab(label='描述性统计', value='descriptive', children=[
                html.Div([
                    html.H2("描述性统计分析", className="section-title"),
                    html.Div(id='descriptive-stats-table')
                ])
            ]),
            dcc.Tab(label='相关性分析', value='correlation', children=[
                html.Div([
                    html.H2("特征相关性分析", className="section-title"),
                    html.Div([
                        html.Label("选择相关系数方法:", className="control-label"),
                        dcc.RadioItems(
                            id='correlation-method',
                            options=[
                                {'label': ' Pearson', 'value': 'pearson'},
                                {'label': ' Spearman', 'value': 'spearman'},
                                {'label': ' Kendall', 'value': 'kendall'}
                            ],
                            value='pearson',
                            inline=True,
                            className="radio-items"
                        )
                    ], className="control-section"),
                    html.Div([dcc.Graph(id='correlation-heatmap')], className="chart-container")
                ])
            ]),
            dcc.Tab(label='数值分布', value='numeric-dist', children=[
                html.Div([
                    html.H2("数值型特征分布分析", className="section-title"),
                    html.Div([
                        html.Label("选择特征:", className="control-label"),
                        dcc.Dropdown(
                            id='numeric-column-selector',
                            options=[],
                            value=None,
                            clearable=False,
                            className="dropdown"
                        )
                    ], className="control-section"),
                    html.Div([
                        html.Label("直方图Bins数量:", className="control-label"),
                        dcc.Slider(
                            id='histogram-bins',
                            min=5,
                            max=50,
                            step=5,
                            value=20,
                            marks={i: str(i) for i in range(5, 51, 10)},
                            className="slider"
                        )
                    ], className="control-section"),
                    html.Div([dcc.Graph(id='numeric-distribution-chart')], className="chart-container")
                ])
            ]),
            dcc.Tab(label='分类分布', value='categorical-dist', children=[
                html.Div([
                    html.H2("分类型特征分布分析", className="section-title"),
                    html.Div([
                        html.Label("选择特征:", className="control-label"),
                        dcc.Dropdown(
                            id='categorical-column-selector',
                            options=[],
                            value=None,
                            clearable=False,
                            className="dropdown"
                        )
                    ], className="control-section"),
                    html.Div([dcc.Graph(id='categorical-distribution-chart')], className="chart-container"),
                    html.H3("频数分布表", className="subsection-title"),
                    html.Div([
                        dash_table.DataTable(
                            id='frequency-table',
                            style_table={'overflowX': 'auto'},
                            style_cell={'textAlign': 'center', 'padding': '10px'},
                            style_header={'backgroundColor': '#f0f2f5', 'fontWeight': 'bold'},
                            page_size=10
                        )
                    ], className="table-container")
                ])
            ]),
            dcc.Tab(label='高级分析', value='advanced', children=[
                html.Div([
                    html.H2("高级分析功能", className="section-title"),
                    html.Div([
                        html.H3("分组统计 (GroupBy)", className="subsection-title"),
                        html.Div([
                            html.Label("选择分组列:", className="control-label"),
                            dcc.Dropdown(id='groupby-column', options=[], value=None, clearable=False, className="dropdown")
                        ], className="control-section half"),
                        html.Div([
                            html.Label("选择聚合列:", className="control-label"),
                            dcc.Dropdown(id='groupby-aggregate-column', options=[], value=None, clearable=False, className="dropdown")
                        ], className="control-section half"),
                        html.Div([
                            html.Label("选择聚合函数:", className="control-label"),
                            dcc.Checklist(
                                id='groupby-functions',
                                options=[
                                    {'label': ' 均值 (mean)', 'value': 'mean'},
                                    {'label': ' 求和 (sum)', 'value': 'sum'},
                                    {'label': ' 计数 (count)', 'value': 'count'},
                                    {'label': ' 最大值 (max)', 'value': 'max'},
                                    {'label': ' 最小值 (min)', 'value': 'min'},
                                    {'label': ' 标准差 (std)', 'value': 'std'}
                                ],
                                value=['mean'],
                                inline=True,
                                className="checklist"
                            )
                        ], className="control-section"),
                        html.Button('执行分组统计', id='groupby-button', className="action-button"),
                        html.Div([
                            dash_table.DataTable(
                                id='groupby-result',
                                style_table={'overflowX': 'auto'},
                                style_cell={'textAlign': 'center', 'padding': '10px'},
                                style_header={'backgroundColor': '#f0f2f5', 'fontWeight': 'bold'},
                                page_size=10
                            )
                        ], className="table-container")
                    ], className="advanced-section"),
                    html.Hr(),
                    html.Div([
                        html.H3("透视表分析 (Pivot Table)", className="subsection-title"),
                        html.Div([
                            html.Label("选择行索引:", className="control-label"),
                            dcc.Dropdown(id='pivot-index', options=[], value=None, clearable=False, className="dropdown")
                        ], className="control-section third"),
                        html.Div([
                            html.Label("选择列索引:", className="control-label"),
                            dcc.Dropdown(id='pivot-columns', options=[], value=None, clearable=False, className="dropdown")
                        ], className="control-section third"),
                        html.Div([
                            html.Label("选择值列:", className="control-label"),
                            dcc.Dropdown(id='pivot-values', options=[], value=None, clearable=False, className="dropdown")
                        ], className="control-section third"),
                        html.Div([
                            html.Label("选择聚合函数:", className="control-label"),
                            dcc.RadioItems(
                                id='pivot-aggfunc',
                                options=[
                                    {'label': ' 均值', 'value': 'mean'},
                                    {'label': ' 求和', 'value': 'sum'},
                                    {'label': ' 计数', 'value': 'count'},
                                    {'label': ' 最大值', 'value': 'max'},
                                    {'label': ' 最小值', 'value': 'min'}
                                ],
                                value='mean',
                                inline=True,
                                className="radio-items"
                            )
                        ], className="control-section"),
                        html.Button('生成透视表', id='pivot-button', className="action-button"),
                        html.Div([
                            dash_table.DataTable(
                                id='pivot-result',
                                style_table={'overflowX': 'auto'},
                                style_cell={'textAlign': 'center', 'padding': '10px'},
                                style_header={'backgroundColor': '#f0f2f5', 'fontWeight': 'bold'},
                                page_size=10
                            )
                        ], className="table-container")
                    ], className="advanced-section")
                ])
            ]),
        ])
    ]),
    
    html.Div(id='loading-overlay', className="loading-overlay", style={'display': 'none'}, children=[
        html.Div([
            html.Span(className="loader"),
            html.P("正在处理数据...")
        ])
    ])
    
], className="main-container")


def parse_file(contents, filename):
    """解析上传的文件并返回DataFrame"""
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return None, "不支持的文件格式"
    except Exception as e:
        return None, f"文件读取错误: {str(e)}"
    
    return df, None


def get_file_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def get_column_types(df):
    """获取列的数据类型"""
    types = {}
    for col in df.columns:
        dtype = df[col].dtype
        if pd.api.types.is_numeric_dtype(dtype):
            if pd.api.types.is_integer_dtype(dtype):
                types[col] = "数值型 (整数)"
            elif pd.api.types.is_float_dtype(dtype):
                types[col] = "数值型 (浮点)"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            types[col] = "日期时间型"
        elif pd.api.types.is_bool_dtype(dtype):
            types[col] = "布尔型"
        else:
            types[col] = "分类型"
    return types


@callback(
    [Output('stored-data', 'data'),
     Output('file-info-store', 'data'),
     Output('file-info-display', 'children'),
     Output('analysis-content', 'style'),
     Output('numeric-column-selector', 'options'),
     Output('numeric-column-selector', 'value'),
     Output('categorical-column-selector', 'options'),
     Output('categorical-column-selector', 'value'),
     Output('groupby-column', 'options'),
     Output('groupby-column', 'value'),
     Output('groupby-aggregate-column', 'options'),
     Output('groupby-aggregate-column', 'value'),
     Output('pivot-index', 'options'),
     Output('pivot-index', 'value'),
     Output('pivot-columns', 'options'),
     Output('pivot-columns', 'value'),
     Output('pivot-values', 'options'),
     Output('pivot-values', 'value')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_output(contents, filename):
    if contents is None:
        return (no_update, no_update, no_update, {'display': 'none'}, 
                [], None, [], None, [], None, [], None, 
                [], None, [], None, [], None)
    
    df, error = parse_file(contents, filename)
    
    if error:
        return (no_update, no_update, html.Div(error, className="error-message"), {'display': 'none'},
                [], None, [], None, [], None, [], None, 
                [], None, [], None, [], None)
    
    file_size = len(base64.b64decode(contents.split(',')[1]))
    
    file_info = {
        'name': filename,
        'size': get_file_size(file_size),
        'format': filename.split('.')[-1].upper(),
        'rows': len(df),
        'columns': len(df.columns)
    }
    
    df_json = df.to_json(date_format='iso', orient='split')
    
    file_info_display = html.Div([
        html.Div([
            html.Span("文件名: ", className="info-label"),
            html.Span(filename, className="info-value")
        ]),
        html.Div([
            html.Span("文件大小: ", className="info-label"),
            html.Span(file_info['size'], className="info-value")
        ]),
        html.Div([
            html.Span("文件格式: ", className="info-label"),
            html.Span(file_info['format'], className="info-value")
        ])
    ], className="file-info-content")
    
    numeric_cols = [{'label': col, 'value': col} for col in df.select_dtypes(include=['number']).columns.tolist()]
    categorical_cols = [{'label': col, 'value': col} for col in df.select_dtypes(include=['object', 'category']).columns.tolist()]
    
    default_numeric = numeric_cols[0]['value'] if numeric_cols else None
    default_categorical = categorical_cols[0]['value'] if categorical_cols else None
    
    pivot_col_default = categorical_cols[1]['value'] if len(categorical_cols) > 1 else None
    
    return (df_json, file_info, file_info_display, 
            {'display': 'block'},
            numeric_cols, default_numeric,
            categorical_cols, default_categorical,
            categorical_cols, default_categorical,
            numeric_cols, default_numeric,
            categorical_cols, default_categorical,
            categorical_cols, pivot_col_default,
            numeric_cols, default_numeric)


@callback(
    [Output('overview-stats', 'children'),
     Output('overview-types-table', 'children'),
     Output('overview-preview-table', 'children')],
    [Input('stored-data', 'data')]
)
def render_data_overview(data):
    if data is None:
        return no_update, no_update, no_update
    
    df = pd.read_json(data, orient='split')
    
    total_rows = len(df)
    total_cols = len(df.columns)
    memory_usage = df.memory_usage(deep=True).sum()
    memory_mb = memory_usage / (1024 * 1024)
    
    stats = html.Div([
        html.Div([
            html.Div("总行数", className="stat-card-label"),
            html.Div(f"{total_rows:,}", className="stat-card-value")
        ], className="stat-card"),
        html.Div([
            html.Div("总列数", className="stat-card-label"),
            html.Div(f"{total_cols}", className="stat-card-value")
        ], className="stat-card"),
        html.Div([
            html.Div("内存占用", className="stat-card-label"),
            html.Div(f"{memory_mb:.2f} MB", className="stat-card-value")
        ], className="stat-card"),
    ], className="stats-row")
    
    col_types = get_column_types(df)
    type_df = pd.DataFrame([
        {'列名': col, '数据类型': col_types[col]} 
        for col in df.columns
    ])
    
    types_table = html.Div([
        html.H3("列数据类型", className="subsection-title"),
        dash_table.DataTable(
            data=type_df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in type_df.columns],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': '#f0f2f5', 'fontWeight': 'bold'},
            page_size=15
        )
    ], className="table-container")
    
    preview_df = df.head(10)
    preview_table = html.Div([
        html.H3("数据预览 (前10行)", className="subsection-title"),
        dash_table.DataTable(
            data=preview_df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in preview_df.columns],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '8px', 'fontSize': '13px'},
            style_header={'backgroundColor': '#f0f2f5', 'fontWeight': 'bold'},
            page_size=10
        )
    ], className="table-container")
    
    return stats, types_table, preview_table


@callback(
    [Output('missing-table', 'children'),
     Output('missing-chart', 'figure')],
    [Input('stored-data', 'data')]
)
def render_missing_values(data):
    if data is None:
        return no_update, {}
    
    df = pd.read_json(data, orient='split')
    
    missing_stats = []
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        missing_ratio = (missing_count / len(df)) * 100
        missing_stats.append({
            '列名': col,
            '缺失值数量': missing_count,
            '缺失比例 (%)': round(missing_ratio, 2)
        })
    
    missing_df = pd.DataFrame(missing_stats)
    
    table = html.Div([
        html.H3("缺失值统计", className="subsection-title"),
        dash_table.DataTable(
            data=missing_df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in missing_df.columns],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': '#f0f2f5', 'fontWeight': 'bold'},
            page_size=15
        )
    ], className="table-container")
    
    df_missing = missing_df[missing_df['缺失值数量'] > 0]
    
    if len(df_missing) == 0:
        fig = go.Figure().update_layout(
            title="无缺失值",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
    else:
        fig = px.bar(
            df_missing, 
            x='列名', 
            y='缺失值数量',
            title='各列缺失值数量',
            labels={'缺失值数量': '缺失值数量', '列名': '列名'},
            color='缺失值数量',
            color_continuous_scale='Reds'
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif"),
            title_font=dict(size=20)
        )
    
    return table, fig


@callback(
    Output('descriptive-stats-table', 'children'),
    [Input('stored-data', 'data')]
)
def render_descriptive_stats(data):
    if data is None:
        return no_update
    
    df = pd.read_json(data, orient='split')
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if not numeric_cols:
        return html.P("数据集中没有数值型特征可供分析", className="no-data-message")
    
    desc_stats = df[numeric_cols].describe().T
    desc_stats = desc_stats.reset_index()
    desc_stats.columns = ['列名', '计数', '均值', '标准差', '最小值', '25%分位', '50%分位', '75%分位', '最大值']
    desc_stats = desc_stats.round(4)
    
    return html.Div([
        html.H3("数值型特征统计", className="subsection-title"),
        dash_table.DataTable(
            data=desc_stats.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in desc_stats.columns],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'padding': '10px'},
            style_header={'backgroundColor': '#f0f2f5', 'fontWeight': 'bold'},
            page_size=15
        )
    ], className="table-container")


@callback(
    Output('correlation-heatmap', 'figure'),
    [Input('correlation-method', 'value'),
     Input('stored-data', 'data')]
)
def update_correlation_heatmap(method, data):
    if data is None:
        return {}
    
    df = pd.read_json(data, orient='split')
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) < 2:
        return go.Figure().update_layout(
            title="至少有2个数值型特征才能计算相关性",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
    
    corr = df[numeric_cols].corr(method=method)
    
    fig = px.imshow(
        corr,
        text_auto='.2f',
        aspect="auto",
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1,
        title=f'{method.capitalize()}相关系数热力图'
    )
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif"),
        title_font=dict(size=20)
    )
    return fig


@callback(
    Output('numeric-distribution-chart', 'figure'),
    [Input('numeric-column-selector', 'value'),
     Input('histogram-bins', 'value'),
     Input('stored-data', 'data')]
)
def update_numeric_distribution(column, bins, data):
    if data is None or column is None:
        return {}
    
    df = pd.read_json(data, orient='split')
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(f'{column} 直方图', f'{column} 分布'),
        specs=[[{"type": "histogram"}, {"type": "bar"}]]
    )
    
    fig.add_trace(
        go.Histogram(
            x=df[column].dropna(),
            nbinsx=bins,
            name='直方图',
            marker_color='#4a90d9',
            opacity=0.7
        ),
        row=1, col=1
    )
    
    kde_x = df[column].dropna()
    if len(kde_x) > 1:
        kde_values = kde_x.value_counts().sort_index()
        fig.add_trace(
            go.Bar(
                x=kde_values.index,
                y=kde_values.values,
                name='分布',
                marker_color='#4a90d9',
                opacity=0.7
            ),
            row=1, col=2
        )
    
    fig.update_layout(
        title_text=f'{column} 分布分析',
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif")
    )
    
    return fig


@callback(
    [Output('categorical-distribution-chart', 'figure'),
     Output('frequency-table', 'data'),
     Output('frequency-table', 'columns')],
    [Input('categorical-column-selector', 'value'),
     Input('stored-data', 'data')]
)
def update_categorical_distribution(column, data):
    if data is None or column is None:
        return {}, [], []
    
    df = pd.read_json(data, orient='split')
    
    value_counts = df[column].value_counts().reset_index()
    value_counts.columns = [column, '频数']
    value_counts['比例 (%)'] = (value_counts['频数'] / len(df) * 100).round(2)
    
    fig = px.bar(
        value_counts.head(20),
        x=column,
        y='频数',
        title=f'{column} 频数分布',
        color='频数',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif"),
        title_font=dict(size=20),
        xaxis_tickangle=-45
    )
    
    table_data = value_counts.to_dict('records')
    table_columns = [{'name': i, 'id': i} for i in value_counts.columns]
    
    return fig, table_data, table_columns


@callback(
    [Output('groupby-result', 'data'),
     Output('groupby-result', 'columns')],
    [Input('groupby-button', 'n_clicks')],
    [State('groupby-column', 'value'),
     State('groupby-aggregate-column', 'value'),
     State('groupby-functions', 'value'),
     State('stored-data', 'data')]
)
def execute_groupby(n_clicks, group_col, agg_col, functions, data):
    if n_clicks is None or data is None or group_col is None or agg_col is None or not functions:
        return [], []
    
    df = pd.read_json(data, orient='split')
    
    try:
        result = df.groupby(group_col)[agg_col].agg(functions).reset_index()
        
        data_records = result.to_dict('records')
        columns = [{'name': i, 'id': i} for i in result.columns]
        
        return data_records, columns
    except Exception as e:
        return [], []


@callback(
    [Output('pivot-result', 'data'),
     Output('pivot-result', 'columns')],
    [Input('pivot-button', 'n_clicks')],
    [State('pivot-index', 'value'),
     State('pivot-columns', 'value'),
     State('pivot-values', 'value'),
     State('pivot-aggfunc', 'value'),
     State('stored-data', 'data')]
)
def execute_pivot(n_clicks, index_col, columns_col, values_col, aggfunc, data):
    if n_clicks is None or data is None or index_col is None or values_col is None:
        return [], []
    
    df = pd.read_json(data, orient='split')
    
    try:
        result = pd.pivot_table(
            df,
            index=index_col,
            columns=columns_col if columns_col else None,
            values=values_col,
            aggfunc=aggfunc
        ).reset_index()
        
        data_records = result.to_dict('records')
        columns = [{'name': str(i), 'id': str(i)} for i in result.columns]
        
        return data_records, columns
    except Exception as e:
        return [], []


app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .main-container {
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }
            
            .app-title {
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 600;
            }
            
            .app-subtitle {
                font-size: 1.1em;
                opacity: 0.9;
            }
            
            .upload-section {
                padding: 40px;
                background: #f8f9fa;
            }
            
            .upload-container {
                border: 3px dashed #667eea;
                border-radius: 15px;
                padding: 50px;
                text-align: center;
                background: white;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .upload-container:hover {
                border-color: #764ba2;
                background: #f0f0ff;
                transform: scale(1.02);
            }
            
            .upload-icon {
                font-size: 4em;
                color: #667eea;
                margin-bottom: 20px;
                display: block;
            }
            
            .upload-container p {
                color: #555;
                font-size: 1.1em;
            }
            
            .upload-hint {
                color: #999 !important;
                font-size: 0.9em !important;
                margin-top: 10px !important;
            }
            
            .file-info {
                padding: 20px 40px;
                background: #e8f5e9;
                border-top: 1px solid #c8e6c9;
            }
            
            .file-info-content {
                display: flex;
                gap: 30px;
                flex-wrap: wrap;
            }
            
            .file-info-content div {
                display: flex;
                gap: 8px;
            }
            
            .info-label {
                font-weight: 600;
                color: #2e7d32;
            }
            
            .info-value {
                color: #1b5e20;
            }
            
            .tab-content {
                padding: 20px;
            }
            
            .error-message {
                padding: 40px;
                text-align: center;
                color: #d32f2f;
                background: #ffebee;
                margin: 20px 40px;
                border-radius: 10px;
            }
            
            .no-data-message {
                text-align: center;
                color: #666;
                padding: 40px;
                font-size: 1.1em;
            }
            
            .section-title {
                color: #333;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #667eea;
            }
            
            .subsection-title {
                color: #555;
                margin: 25px 0 15px;
            }
            
            .stats-row {
                display: flex;
                gap: 20px;
                margin-bottom: 30px;
                flex-wrap: wrap;
            }
            
            .stat-card {
                flex: 1;
                min-width: 150px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            }
            
            .stat-card-label {
                font-size: 0.9em;
                opacity: 0.9;
                margin-bottom: 10px;
            }
            
            .stat-card-value {
                font-size: 2em;
                font-weight: 600;
            }
            
            .table-container {
                overflow-x: auto;
                margin: 15px 0;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }
            
            .chart-container {
                margin: 20px 0;
                border-radius: 15px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }
            
            .control-section {
                margin: 20px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 10px;
            }
            
            .control-section.half {
                width: calc(50% - 10px);
                display: inline-block;
                vertical-align: top;
            }
            
            .control-section.third {
                width: calc(33.33% - 14px);
                display: inline-block;
                vertical-align: top;
                margin-right: 15px;
            }
            
            .control-label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #333;
            }
            
            .dropdown {
                border-radius: 8px;
            }
            
            .slider {
                padding: 10px 0;
            }
            
            .radio-items {
                padding: 10px 0;
            }
            
            .checklist {
                padding: 10px 0;
            }
            
            .action-button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 25px;
                font-size: 1em;
                cursor: pointer;
                transition: all 0.3s ease;
                margin: 15px 0;
            }
            
            .action-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
            }
            
            .advanced-section {
                margin: 30px 0;
            }
            
            .loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(255, 255, 255, 0.9);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 1000;
            }
            
            .loading-overlay div {
                text-align: center;
            }
            
            .loader {
                width: 50px;
                height: 50px;
                border: 5px solid #f3f3f3;
                border-top: 5px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                display: inline-block;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .loading-overlay p {
                margin-top: 20px;
                color: #667eea;
                font-size: 1.2em;
            }
            
            @media (max-width: 768px) {
                .app-title {
                    font-size: 1.8em;
                }
                
                .upload-section {
                    padding: 20px;
                }
                
                .upload-container {
                    padding: 30px;
                }
                
                .stats-row {
                    flex-direction: column;
                }
                
                .control-section.half,
                .control-section.third {
                    width: 100%;
                    margin-right: 0;
                }
                
                .file-info-content {
                    flex-direction: column;
                    gap: 10px;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    import webbrowser
    from threading import Timer
    
    def open_browser():
        webbrowser.open_new("http://127.0.0.1:8050/")
    
    Timer(1, open_browser).start()
    app.run(debug=True, port=8050)
