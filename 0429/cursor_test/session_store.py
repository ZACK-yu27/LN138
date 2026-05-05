"""
服务端会话缓存：上传解析后的 DataFrame 按 session_id 存放，避免通过 dcc.Store 传输大对象。
支持淘汰策略以控制内存。
"""

from __future__ import annotations

import base64
import io
import uuid
from collections import OrderedDict
from typing import Any

import pandas as pd

# 单表最大行数（超出则截断并标记，保证界面可响应）
MAX_ROWS_STORED = 200_000
# 最多保留的会话数量
MAX_SESSIONS = 5


class SessionStore:
    """LRU 式 DataFrame 缓存。"""

    def __init__(self, max_sessions: int = MAX_SESSIONS) -> None:
        self._cache: OrderedDict[str, pd.DataFrame] = OrderedDict()
        self._meta: dict[str, dict[str, Any]] = {}
        self._max = max_sessions

    def put(self, df: pd.DataFrame, meta: dict[str, Any]) -> str:
        """存入 DataFrame，返回 session_id。"""
        sid = str(uuid.uuid4())
        while len(self._cache) >= self._max:
            old_key, _ = self._cache.popitem(last=False)
            self._meta.pop(old_key, None)
        self._cache[sid] = df
        self._meta[sid] = meta
        self._cache.move_to_end(sid)
        return sid

    def touch(self, sid: str) -> None:
        if sid in self._cache:
            self._cache.move_to_end(sid)

    def get(self, sid: str) -> pd.DataFrame | None:
        if sid not in self._cache:
            return None
        self._cache.move_to_end(sid)
        return self._cache[sid]

    def get_meta(self, sid: str) -> dict[str, Any] | None:
        return self._meta.get(sid)

    def clear_session(self, sid: str) -> None:
        self._cache.pop(sid, None)
        self._meta.pop(sid, None)


sessions = SessionStore()


def decode_upload(contents: str) -> bytes:
    """将 dcc.Upload 的 contents 转为原始字节。"""
    _, b64 = contents.split(",", 1)
    return base64.b64decode(b64)


def load_dataframe(filename: str, raw: bytes) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    根据扩展名解析为 DataFrame。

    Returns:
        (df, info): info 含 truncated 布尔、original_rows 等。
    """
    lower = filename.lower()
    bio = io.BytesIO(raw)
    truncated = False
    original_rows: int | None = None

    if lower.endswith(".csv"):
        df = pd.read_csv(bio, encoding_errors="replace")
    elif lower.endswith(".xlsx"):
        df = pd.read_excel(bio, engine="openpyxl")
    elif lower.endswith(".xls"):
        df = pd.read_excel(bio, engine="xlrd")
    else:
        raise ValueError(f"不支持的文件格式: {filename}，请上传 .csv / .xlsx / .xls")

    original_rows = len(df)
    if len(df) > MAX_ROWS_STORED:
        df = df.iloc[:MAX_ROWS_STORED].copy()
        truncated = True

    info = {
        "truncated": truncated,
        "original_rows": original_rows,
        "stored_rows": len(df),
    }
    return df, info
