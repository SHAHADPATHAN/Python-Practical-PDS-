"""
Records service — serves paginated records from balanced_logs.csv
(6.97 MB, safe to load fully) with search/filter/sort support.
"""

from typing import Any, Dict, List, Optional
import math
import numpy as np
import pandas as pd

from backend.utils import cache, paths


def _clean_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = {}
    for k, v in rec.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            cleaned[k] = None
        elif pd.isna(v):
            cleaned[k] = None
        else:
            cleaned[k] = v
    return cleaned


def _load_records_df() -> pd.DataFrame:
    if cache.has("records_df"):
        return cache.get("records_df")

    if not paths.BALANCED_CSV.exists():
        return pd.DataFrame()

    # balanced_logs.csv is 6.97 MB — safe to fully load
    df = pd.read_csv(paths.BALANCED_CSV, low_memory=False)

    # Normalise columns
    df.columns = df.columns.str.strip().str.lower()

    # Parse timestamp if present
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["timestamp_str"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    cache.set("records_df", df)
    return df


def get_records(
    page: int = 1,
    page_size: int = 100,
    label: Optional[str] = None,
    ip: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "timestamp",
    sort_order: str = "asc",
) -> Dict[str, Any]:
    df = _load_records_df()

    if df.empty:
        return {
            "total": 0, "page": page,
            "page_size": page_size, "records": [], "data": [], "columns": [],
        }

    filtered = df.copy()

    # Label filter
    if label and "label" in filtered.columns:
        filtered = filtered[filtered["label"].str.lower() == label.lower()]

    # IP filter
    if ip and "ip" in filtered.columns:
        filtered = filtered[filtered["ip"].astype(str).str.contains(ip, na=False)]

    # Full-text search on user_agent, ip, or label
    if search:
        mask = pd.Series(False, index=filtered.index)
        for col in ["ip", "user_agent", "label", "scanner_type", "bot_type"]:
            if col in filtered.columns:
                mask |= filtered[col].astype(str).str.contains(
                    search, case=False, na=False
                )
        filtered = filtered[mask]

    # Sort
    if sort_by in filtered.columns:
        filtered = filtered.sort_values(
            sort_by,
            ascending=(sort_order.lower() == "asc"),
            na_position="last",
        )

    total = len(filtered)
    start = (page - 1) * page_size
    end   = start + page_size
    page_df = filtered.iloc[start:end]

    # Use string timestamp for JSON serialisation
    if "timestamp_str" in page_df.columns:
        page_df = page_df.drop(columns=["timestamp"], errors="ignore")
        page_df = page_df.rename(columns={"timestamp_str": "timestamp"})

    cols = [
        c for c in page_df.columns
        if c not in ("timestamp_str",)
    ]

    raw_records = page_df[cols].to_dict("records")
    clean_records = [_clean_record(r) for r in raw_records]

    return {
        "total":     total,
        "page":      page,
        "page_size": page_size,
        "columns":   cols,
        "records":   clean_records,
        "data":      clean_records,
    }


def get_record_columns() -> List[str]:
    df = _load_records_df()
    if df.empty:
        return []
    return [c for c in df.columns if c != "timestamp_str"]
