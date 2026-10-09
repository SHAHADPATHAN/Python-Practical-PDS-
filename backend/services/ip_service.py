"""
IP intelligence service.
Reads from ip_summary.csv (~243 KB) which is small enough to keep in memory.
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


def _load_ip_df() -> pd.DataFrame:
    if cache.has("ip_df"):
        return cache.get("ip_df")

    if not paths.IP_SUMMARY_CSV.exists():
        return pd.DataFrame()

    df = pd.read_csv(paths.IP_SUMMARY_CSV)
    df.columns = df.columns.str.strip().str.lower()

    # Normalise expected column names
    if "total_requests" in df.columns:
        df["request_count"] = df["total_requests"]
    elif "requests" in df.columns:
        df["request_count"] = df["requests"]
    else:
        df["request_count"] = 1

    # Derive dominant label from class request counts
    req_cols = {
        "scanner": "scanner_requests",
        "suspicious": "suspicious_requests",
        "benign": "benign_requests",
        "bot": "bot_requests",
    }
    existing_cols = {k: v for k, v in req_cols.items() if v in df.columns}
    if existing_cols:
        def calc_dominant(row):
            counts = {k: row.get(col, 0) or 0 for k, col in existing_cols.items()}
            return max(counts, key=counts.get)
        df["dominant_label"] = df.apply(calc_dominant, axis=1)
    else:
        df["dominant_label"] = "scanner"

    if "unique_labels" not in df.columns:
        df["unique_labels"] = 1

    # Compute risk score
    df = _add_risk_score(df)

    cache.set("ip_df", df)
    return df


def _add_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    """Compute a 0–100 risk score from measurable signals."""
    if df.empty:
        return df

    score = pd.Series(0.0, index=df.index)

    # Request volume (up to 40 pts)
    if "request_count" in df.columns:
        max_req = df["request_count"].max()
        if max_req > 0:
            score += (df["request_count"] / max_req * 40).clip(0, 40)

    # Scanner label (35 pts)
    if "dominant_label" in df.columns:
        score += df["dominant_label"].astype(str).str.lower().eq("scanner").astype(float) * 35

    # Bot label (20 pts)
    if "dominant_label" in df.columns:
        score += df["dominant_label"].astype(str).str.lower().eq("bot").astype(float) * 20

    # Suspicious label (25 pts)
    if "dominant_label" in df.columns:
        score += df["dominant_label"].astype(str).str.lower().eq("suspicious").astype(float) * 25

    df["risk_score"] = score.clip(0, 100).round(1)

    def risk_level(s: float) -> str:
        if s >= 76: return "CRITICAL"
        if s >= 51: return "HIGH"
        if s >= 26: return "MEDIUM"
        return "LOW"

    df["risk_level"] = df["risk_score"].apply(risk_level)
    return df


def get_ip_list(
    page: int = 1,
    page_size: int = 50,
    label: Optional[str] = None,
    sort_by: str = "request_count",
    sort_order: str = "desc",
    search: Optional[str] = None,
) -> Dict[str, Any]:
    df = _load_ip_df()
    if df.empty:
        return {"total": 0, "page": page, "page_size": page_size, "data": []}

    # Filter
    if label:
        if "dominant_label" in df.columns:
            df = df[df["dominant_label"].astype(str).str.lower() == label.lower()]

    if search:
        if "ip" in df.columns:
            df = df[df["ip"].astype(str).str.contains(search, na=False)]

    # Sort
    sort_col = sort_by if sort_by in df.columns else "request_count"
    if sort_col in df.columns:
        df = df.sort_values(sort_col, ascending=(sort_order == "asc"))

    total = len(df)
    start = (page - 1) * page_size
    end   = start + page_size
    page_df = df.iloc[start:end]

    raw_records = page_df.to_dict("records")
    clean_records = [_clean_record(r) for r in raw_records]

    return {
        "total":     total,
        "page":      page,
        "page_size": page_size,
        "data":      clean_records,
    }


def get_ip_detail(ip: str) -> Optional[Dict[str, Any]]:
    df = _load_ip_df()
    if df.empty or "ip" not in df.columns:
        return None

    row = df[df["ip"].astype(str) == ip]
    if row.empty:
        return None

    record = _clean_record(row.iloc[0].to_dict())

    # Add risk factors explanation
    factors = []
    rc = record.get("request_count", 0) or 0
    if rc >= 10_000:
        factors.append("Extremely high request volume")
    elif rc >= 1_000:
        factors.append("High request volume")

    label = str(record.get("dominant_label", "")).lower()
    if label == "scanner":
        factors.append("Scanner tool user-agent detected")
    if label == "bot":
        factors.append("Automated bot client detected")
    if label == "suspicious":
        factors.append("Rapid repeated requests detected")

    record["risk_factors"] = factors
    return record


def get_top_ips(n: int = 10) -> List[Dict[str, Any]]:
    df = _load_ip_df()
    if df.empty:
        return []

    col = "request_count" if "request_count" in df.columns else "total_requests"
    if col not in df.columns:
        col = df.columns[1]
    top = df.nlargest(n, col)
    raw_records = top.to_dict("records")
    return [_clean_record(r) for r in raw_records]
