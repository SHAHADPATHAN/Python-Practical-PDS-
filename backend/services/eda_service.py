"""
EDA service — reads from small pre-aggregated CSVs and report files.
Never loads the full feature dataset.
"""

from typing import Any, Dict, List

import pandas as pd

from backend.utils import cache, paths
from backend.services.dataset_service import DATASET_FACTS


def get_hourly_activity() -> List[Dict[str, Any]]:
    """Return hourly activity time-series from hourly_activity.csv."""
    if cache.has("hourly_activity"):
        return cache.get("hourly_activity")

    if not paths.HOURLY_CSV.exists():
        return []

    df = pd.read_csv(paths.HOURLY_CSV)
    df.columns = df.columns.str.strip().str.lower()

    # Normalise timestamp column
    ts_col = next(
        (c for c in df.columns if "time" in c or "date" in c or "hour" in c),
        df.columns[0]
    )
    df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")
    df = df.sort_values(ts_col)
    df[ts_col] = df[ts_col].dt.strftime("%Y-%m-%d %H:%M")
    df = df.fillna(0)

    result = df.to_dict("records")
    cache.set("hourly_activity", result)
    return result


def get_label_heatmap() -> List[Dict[str, Any]]:
    """Return hourly-label pivot for heatmap from label_hour_pivot.csv."""
    if cache.has("label_heatmap"):
        return cache.get("label_heatmap")

    if not paths.PIVOT_CSV.exists():
        return []

    df = pd.read_csv(paths.PIVOT_CSV)
    df.columns = df.columns.str.strip().str.lower()
    df = df.fillna(0)

    result = df.to_dict("records")
    cache.set("label_heatmap", result)
    return result


def get_requests_by_hour() -> List[Dict[str, Any]]:
    """
    Return fixed hourly request counts from the EDA report.
    These come from practical_08_eda_report.txt (balanced 18,304-row dataset).
    """
    HOURLY_DATA = [
        {"hour": 0,  "requests": 468},
        {"hour": 1,  "requests": 482},
        {"hour": 2,  "requests": 514},
        {"hour": 3,  "requests": 430},
        {"hour": 4,  "requests": 488},
        {"hour": 5,  "requests": 1204},
        {"hour": 6,  "requests": 1157},
        {"hour": 7,  "requests": 1115},
        {"hour": 8,  "requests": 2099},
        {"hour": 9,  "requests": 897},
        {"hour": 10, "requests": 567},
        {"hour": 11, "requests": 503},
        {"hour": 12, "requests": 506},
        {"hour": 13, "requests": 497},
        {"hour": 14, "requests": 1228},
        {"hour": 15, "requests": 1228},
        {"hour": 16, "requests": 1091},
        {"hour": 17, "requests": 997},
        {"hour": 18, "requests": 604},
        {"hour": 19, "requests": 508},
        {"hour": 20, "requests": 389},
        {"hour": 21, "requests": 436},
        {"hour": 22, "requests": 440},
        {"hour": 23, "requests": 456},
    ]
    return HOURLY_DATA


def get_top_ips_eda() -> List[Dict[str, Any]]:
    """
    Return top-10 IPs from the EDA report (balanced dataset).
    From practical_08_eda_report.txt — actual output.
    """
    return [
        {"ip": "212.60.12.161",    "requests": 1491},
        {"ip": "103.111.33.197",   "requests": 765},
        {"ip": "127.0.0.1",        "requests": 757},
        {"ip": "157.32.35.29",     "requests": 719},
        {"ip": "14.139.122.76",    "requests": 693},
        {"ip": "152.58.35.97",     "requests": 653},
        {"ip": "139.162.253.24",   "requests": 512},
        {"ip": "212.71.238.216",   "requests": 421},
        {"ip": "199.188.238.77",   "requests": 312},
        {"ip": "139.144.154.251",  "requests": 305},
    ]


def get_top_scanner_ips() -> List[Dict[str, Any]]:
    """Top scanner IPs from practical_08_eda_report.txt."""
    return [
        {"ip": "212.60.12.161",    "requests": 1491},
        {"ip": "103.111.33.197",   "requests": 765},
        {"ip": "157.32.35.29",     "requests": 719},
        {"ip": "152.58.35.97",     "requests": 653},
        {"ip": "199.188.238.77",   "requests": 312},
        {"ip": "49.36.67.24",      "requests": 151},
        {"ip": "49.36.64.212",     "requests": 125},
        {"ip": "143.244.44.163",   "requests": 59},
        {"ip": "152.58.60.21",     "requests": 56},
        {"ip": "106.205.210.163",  "requests": 53},
    ]


def get_hourly_heatmap_matrix() -> Dict[str, Any]:
    """Return heatmap data structured for frontend charting."""
    HEATMAP = [
        {"hour": 0,  "benign": 169, "bot": 246, "scanner": 0,   "suspicious": 53},
        {"hour": 1,  "benign": 187, "bot": 207, "scanner": 0,   "suspicious": 88},
        {"hour": 2,  "benign": 191, "bot": 143, "scanner": 86,  "suspicious": 94},
        {"hour": 3,  "benign": 215, "bot": 155, "scanner": 1,   "suspicious": 59},
        {"hour": 4,  "benign": 208, "bot": 192, "scanner": 1,   "suspicious": 87},
        {"hour": 5,  "benign": 206, "bot": 350, "scanner": 498, "suspicious": 150},
        {"hour": 6,  "benign": 190, "bot": 148, "scanner": 741, "suspicious": 78},
        {"hour": 7,  "benign": 262, "bot": 116, "scanner": 298, "suspicious": 439},
        {"hour": 8,  "benign": 189, "bot": 164, "scanner": 35,  "suspicious": 1711},
        {"hour": 9,  "benign": 184, "bot": 219, "scanner": 26,  "suspicious": 468},
        {"hour": 10, "benign": 203, "bot": 127, "scanner": 7,   "suspicious": 230},
        {"hour": 11, "benign": 190, "bot": 195, "scanner": 1,   "suspicious": 117},
        {"hour": 12, "benign": 188, "bot": 262, "scanner": 15,  "suspicious": 41},
        {"hour": 13, "benign": 195, "bot": 173, "scanner": 84,  "suspicious": 45},
        {"hour": 14, "benign": 141, "bot": 228, "scanner": 794, "suspicious": 65},
        {"hour": 15, "benign": 195, "bot": 113, "scanner": 840, "suspicious": 80},
        {"hour": 16, "benign": 175, "bot": 272, "scanner": 569, "suspicious": 75},
        {"hour": 17, "benign": 181, "bot": 185, "scanner": 386, "suspicious": 245},
        {"hour": 18, "benign": 205, "bot": 147, "scanner": 192, "suspicious": 60},
        {"hour": 19, "benign": 176, "bot": 256, "scanner": 1,   "suspicious": 75},
        {"hour": 20, "benign": 182, "bot": 122, "scanner": 0,   "suspicious": 85},
        {"hour": 21, "benign": 182, "bot": 196, "scanner": 0,   "suspicious": 58},
        {"hour": 22, "benign": 169, "bot": 184, "scanner": 1,   "suspicious": 86},
        {"hour": 23, "benign": 193, "bot": 176, "scanner": 0,   "suspicious": 87},
    ]
    return {"heatmap": HEATMAP, "peak_date": "2024-01-18", "daily_time_points": 408}


def get_eda_summary() -> Dict[str, Any]:
    return {
        "dataset": "balanced_logs.csv",
        "rows_analyzed": 18_304,
        "columns_analyzed": 53,
        "peak_date": "2024-01-18",
        "peak_daily_requests": 2_733,
        "bot_records": 4_576,
        "internal_ip_records": 757,
        "hourly_time_points": 9_782,
        "daily_time_points": 408,
        "status_code_available": False,
        "status_code_note": "cj.log does not contain an HTTP status-code field.",
    }
