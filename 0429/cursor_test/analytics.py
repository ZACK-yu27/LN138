"""
数据分析纯函数：输入 pandas DataFrame，返回表格/图表所需结构。
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def memory_usage_mb(df: pd.DataFrame) -> float:
    """DataFrame 内存占用（MB）。"""
    return float(df.memory_usage(deep=True).sum() / (1024**2))


def dtype_category(dtype: Any) -> str:
    """将 pandas dtype 归为业务类别。"""
    if pd.api.types.is_numeric_dtype(dtype):
        return "数值型"
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "日期时间"
    if pd.api.types.is_bool_dtype(dtype):
        return "布尔型"
    return "分类型"


def basic_overview(df: pd.DataFrame) -> dict[str, Any]:
    """基本概览：行列数、类型表、内存、前 10 行。"""
    type_rows = []
    for col in df.columns:
        type_rows.append(
            {
                "列名": col,
                "pandas类型": str(df[col].dtype),
                "业务类型": dtype_category(df[col].dtype),
            }
        )
    preview = df.head(10)
    return {
        "n_rows": len(df),
        "n_cols": len(df.columns),
        "memory_mb": round(memory_usage_mb(df), 4),
        "types": type_rows,
        "preview_columns": [{"name": c, "id": c} for c in df.columns],
        "preview_data": preview.replace({np.nan: None}).to_dict("records"),
    }


def missing_analysis(df: pd.DataFrame) -> dict[str, Any]:
    """缺失值数量与比例。"""
    n = len(df)
    rows = []
    for col in df.columns:
        miss = int(df[col].isna().sum())
        pct = round(100.0 * miss / n, 4) if n else 0.0
        rows.append({"列名": col, "缺失数量": miss, "缺失比例(%)": pct})
    return {"rows": rows, "total_rows": n}


def describe_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """数值列描述性统计。"""
    num = df.select_dtypes(include=["number"])
    if num.empty:
        return pd.DataFrame()
    desc = num.describe(percentiles=[0.25, 0.5, 0.75]).T
    desc = desc.rename(
        columns={
            "mean": "均值",
            "std": "标准差",
            "min": "最小值",
            "25%": "Q1",
            "50%": "中位数",
            "75%": "Q3",
            "max": "最大值",
        }
    )
    return desc


def correlation_matrix(
    df: pd.DataFrame, method: str = "pearson"
) -> tuple[pd.DataFrame, list[str]]:
    """数值列相关系数矩阵。"""
    num = df.select_dtypes(include=["number"])
    if num.shape[1] < 2:
        return pd.DataFrame(), list(num.columns)
    corr = num.corr(method=method, numeric_only=True)
    return corr, list(corr.columns)


def sample_for_plot(series: pd.Series, max_points: int = 50_000) -> pd.Series:
    """大图下采样以减轻前端负担。"""
    s = series.dropna()
    if len(s) <= max_points:
        return s
    return s.sample(n=max_points, random_state=42)


def categorical_frequency(df: pd.DataFrame, column: str, top_n: int = 30) -> pd.DataFrame:
    """单列频数，限制 Top N 类别。"""
    vc = df[column].value_counts(dropna=False).head(top_n)
    out = vc.reset_index()
    out.columns = ["类别", "频数"]
    out["比例(%)"] = (out["频数"] / len(df) * 100).round(4)
    return out


def run_groupby(
    df: pd.DataFrame,
    group_cols: list[str],
    agg_col: str,
    agg_func: str,
) -> pd.DataFrame:
    """pandas groupby 聚合。"""
    if not group_cols:
        raise ValueError("请至少选择一列作为分组列")
    if agg_col not in df.columns:
        raise ValueError("聚合列无效")
    g = df.groupby(group_cols, dropna=False)[agg_col]
    func_map = {
        "sum": "sum",
        "mean": "mean",
        "median": "median",
        "min": "min",
        "max": "max",
        "count": "count",
        "std": "std",
        "nunique": "nunique",
    }
    if agg_func not in func_map:
        raise ValueError("不支持的聚合函数")
    out = getattr(g, func_map[agg_func])()
    if isinstance(out, pd.Series):
        out = out.reset_index()
    else:
        out = out.reset_index()
    return out


def run_pivot(
    df: pd.DataFrame,
    index: str | None,
    columns: str | None,
    values: str,
    aggfunc: str = "mean",
) -> pd.DataFrame:
    """透视表。"""
    if not values or values not in df.columns:
        raise ValueError("请选择有效的值字段")
    idx = index if index else None
    cols = columns if columns else None
    agg_map = {
        "mean": "mean",
        "sum": "sum",
        "count": "count",
        "min": "min",
        "max": "max",
        "median": "median",
    }
    if aggfunc not in agg_map:
        raise ValueError("不支持的聚合方式")
    pt = pd.pivot_table(
        df,
        values=values,
        index=idx,
        columns=cols,
        aggfunc=agg_map[aggfunc],
        fill_value=None,
    )
    return pt.reset_index() if idx is not None else pt
