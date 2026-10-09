"""
Upload and analysis pipeline service.
Handles file uploads, format detection, parsing, cleaning,
feature engineering, labeling, risk scoring, and ML prediction.
"""

import math
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from backend.parsers.log_parser import (
    UniversalWebLogParser,
    detect_format,
    get_parser_by_name,
)
from backend.utils import cache, paths

# Scanner / bot patterns (mirrors practical_10_pipeline.py)
SCANNER_PATTERNS = [
    "gobuster", "dirbuster", "nmap", "nikto",
    "zgrab", "nessus", "masscan", "wpscan",
    "sqlmap", "acunetix", "nuclei", "openvas", "burp",
]

BOT_PATTERNS = [
    "python-requests", "go-http-client",
    "bot", "spider", "curl", "crawler", "scrapy", "wget", "urllib",
]

BROWSER_PATTERNS = [
    "mozilla", "chrome", "firefox", "safari", "edge", "opera",
]

PATH_ATTACK_PATTERNS = [
    "wp-config", ".env", "etc/passwd", "setup.cgi", "union+select",
    "union select", "../", "..\\", "cmd.exe", "/bin/sh", "/bin/bash",
    "<script", "phpinfo", "eval(", "actuator", ".git/", "xmlrpc.php",
]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _detect_scanner(ua: str, path: str = "") -> str:
    text = str(ua).lower()
    for p in SCANNER_PATTERNS:
        if p in text:
            return p
    path_text = str(path).lower()
    for p in PATH_ATTACK_PATTERNS:
        if p in path_text:
            return f"path_attack:{p}"
    return "none"


def _detect_bot(ua: str) -> str:
    text = str(ua).lower()
    for p in BOT_PATTERNS:
        if p in text:
            return p
    return "none"


def _is_browser(ua: str) -> bool:
    text = str(ua).lower()
    return any(p in text for p in BROWSER_PATTERNS)


def _string_entropy(value) -> float:
    if not value or pd.isna(value):
        return 0.0
    s = str(value)
    if not s:
        return 0.0
    from collections import Counter
    counts = Counter(s)
    length = len(s)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())


def _classify(scanner_type: str, bot_type: str, rapid: bool) -> str:
    if scanner_type != "none":
        return "scanner"
    if bot_type != "none":
        return "bot"
    if rapid:
        return "suspicious"
    return "benign"


def _compute_risk(row: pd.Series) -> float:
    score = 0.0
    rc = row.get("requests_per_ip", 0) or 0
    score += min(40, rc / 500 * 40)
    up = row.get("unique_ports_per_ip", 0) or 0
    score += min(20, up / 10 * 20)
    if row.get("is_scanner", False):
        score += 35
    if row.get("is_bot", False):
        score += 15
    if row.get("rapid_request_1s", False):
        score += 15
    return round(min(100.0, score), 1)


def _risk_level(score: float) -> str:
    if score >= 76: return "CRITICAL"
    if score >= 51: return "HIGH"
    if score >= 26: return "MEDIUM"
    return "LOW"


def _parse_timestamp_series(series: pd.Series) -> pd.Series:
    """Parse timestamps with multiple fallback formats (ISO, Apache, custom)."""
    try:
        parsed = pd.to_datetime(series, utc=True, errors="coerce")
    except Exception:
        parsed = pd.Series([pd.NaT] * len(series), index=series.index)

    if parsed.isna().sum() > len(series) * 0.4:
        for fmt in [
            "%d/%b/%Y:%H:%M:%S %z",
            "%d/%b/%Y:%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S%z",
        ]:
            try:
                alt = pd.to_datetime(series, format=fmt, utc=True, errors="coerce")
                if alt.isna().sum() < parsed.isna().sum():
                    parsed = alt
                    if parsed.isna().sum() == 0:
                        break
            except Exception:
                continue
    return parsed


def _clean_record(d: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all record values are strictly JSON compliant (no Timestamps, no NaNs)."""
    clean: Dict[str, Any] = {}
    for k, v in d.items():
        if v is None or pd.isna(v):
            clean[k] = None
        elif isinstance(v, (pd.Timestamp,)):
            clean[k] = str(v)
        elif hasattr(v, "isoformat"):
            clean[k] = v.isoformat()
        elif isinstance(v, (np.integer,)):
            clean[k] = int(v)
        elif isinstance(v, (np.floating, float)):
            clean[k] = None if (math.isnan(v) or math.isinf(v)) else round(float(v), 4)
        elif isinstance(v, (np.bool_,)):
            clean[k] = bool(v)
        else:
            clean[k] = v
    return clean


def extract_json_records(data: Any) -> List[Dict[str, Any]]:
    """
    Extract log or security findings records from arbitrary JSON documents
    (e.g., OWASP crAPI benchmark, DAST/SAST reports, Wazuh/Suricata JSON,
     arrays of events, or single JSON events).
    """
    records: List[Dict[str, Any]] = []
    top_ts = "2024-01-01T12:00:00"
    if isinstance(data, dict):
        top_ts = str(data.get("timestamp") or data.get("start_time") or data.get("date") or top_ts)
        target_list = None
        for k in [
            "findings_detail", "findings", "results", "records", "events",
            "items", "vulnerabilities", "alerts", "logs", "data", "entries",
            "hits", "issues", "tests", "scans", "transactions"
        ]:
            if k in data and isinstance(data[k], list) and len(data[k]) > 0:
                target_list = data[k]
                break
        if target_list is None:
            for v in data.values():
                if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                    target_list = v
                    break
        items = target_list if target_list is not None else [data]
    elif isinstance(data, list):
        items = data
    else:
        return []

    from urllib.parse import urlparse

    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            if isinstance(item, list) and len(item) >= 4:
                from backend.parsers.log_parser import CJLogParser
                cj_p = CJLogParser()
                import json as _json
                rec = cj_p.parse_line(_json.dumps(item))
                if rec:
                    records.append(rec)
            continue

        raw_url = item.get("url") or item.get("path") or item.get("uri") or item.get("endpoint") or "/"
        parsed = urlparse(str(raw_url))
        host = (
            item.get("ip") or item.get("client_ip") or item.get("host")
            or item.get("source_ip") or item.get("src_ip")
            or parsed.hostname or "localhost"
        )
        path = parsed.path if parsed.path else str(raw_url)
        if parsed.query:
            path += "?" + parsed.query

        status = (
            item.get("http_status") or item.get("status_code")
            or item.get("response_code") or item.get("status") or 200
        )
        if isinstance(status, str) and not status.isdigit():
            status = 200 if status.upper() in ("VERIFIED", "LIKELY", "SUCCESS") else 404
        else:
            try: status = int(status)
            except Exception: status = 200

        method = item.get("method") or item.get("http_method") or "GET"
        ua = (
            item.get("user_agent") or item.get("test_id")
            or item.get("agent") or item.get("scanner") or "SecurityScanner/1.0"
        )

        is_confirmed = (
            item.get("is_confirmed") is True
            or str(item.get("status")).upper() in ("VERIFIED", "LIKELY", "VULNERABLE", "CONFIRMED", "HIGH", "CRITICAL")
            or str(item.get("severity", "")).upper() in ("HIGH", "CRITICAL")
        )

        vuln_type = str(item.get("vuln_type") or item.get("rule_id") or item.get("title") or "none").lower()
        scanner_type = vuln_type if is_confirmed else "none"

        risk_val = item.get("risk_score") or item.get("confidence")
        if risk_val is not None:
            try:
                r_num = float(risk_val)
                risk_score = round(r_num * 100 if r_num <= 1.0 else r_num, 1)
            except Exception:
                risk_score = 90.0 if is_confirmed else 20.0
        else:
            risk_score = 90.0 if is_confirmed else 20.0

        label = "scanner" if is_confirmed else "benign"

        meta_text = (
            item.get("reason") or item.get("description")
            or item.get("message") or item.get("matched_ground_truth") or ""
        )

        records.append({
            "timestamp": str(item.get("timestamp") or item.get("time") or top_ts),
            "ip": str(host),
            "method": str(method).upper(),
            "path": str(path),
            "status": int(status),
            "user_agent": str(ua),
            "scanner_type": scanner_type,
            "is_scanner": is_confirmed,
            "label": label,
            "risk_score": risk_score,
            "metadata": str(meta_text),
        })

    return records


# ─── Main analysis pipeline ───────────────────────────────────────────────────

def analyze_upload(
    file_path: Path,
    parser_hint: Optional[str] = None,
    max_records: int = 200_000,
) -> Dict[str, Any]:
    """
    Full pipeline on an uploaded log file.
    Returns a complete, strictly JSON-serializable analysis result dict.
    """
    # 0. Check if file is a whole-document JSON (indented JSON, security benchmark report, or JSON array)
    records: List[Dict[str, Any]] = []
    invalid_count = 0
    total_lines   = 0
    detected_format = "universal"
    parser_name = "universal"
    is_json_doc = False
    parser = None

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        stripped = content.strip()
        total_lines = content.count("\n") + 1
        if stripped.startswith(("{", "[")):
            try:
                import json as _json
                data = _json.loads(stripped)
                json_recs = extract_json_records(data)
                if json_recs:
                    records = json_recs
                    detected_format = "json"
                    parser_name = "JSON Security Findings Report"
                    valid_count = len(records)
                    invalid_count = 0
                    is_json_doc = True
            except Exception:
                pass
    except Exception:
        pass

    if not is_json_doc:
        # 1. Read sample lines for format detection
        sample_lines: List[str] = []
        with file_path.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                stripped_line = line.strip()
                if stripped_line:
                    sample_lines.append(stripped_line)
                if len(sample_lines) >= 50:
                    break

        # 2. Select initial parser
        if parser_hint:
            parser = get_parser_by_name(parser_hint) or detect_format(sample_lines)
        else:
            parser = detect_format(sample_lines)

        detected_format = parser.FORMAT_NAME
        parser_name = parser.FORMAT_NAME

        # 3. Parse records
        total_lines = 0
        with file_path.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                total_lines += 1
                stripped_line = line.strip()
                if not stripped_line:
                    continue
                rec = parser.parse_line(stripped_line)
                if rec is None:
                    invalid_count += 1
                else:
                    records.append(rec)
                if len(records) >= max_records:
                    break

        # Fallback to UniversalWebLogParser if hint or initial parser parsed 0 lines
        if len(records) == 0 and not isinstance(parser, UniversalWebLogParser):
            fallback_parser = UniversalWebLogParser()
            records = []
            invalid_count = 0
            total_lines = 0
            with file_path.open("r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    total_lines += 1
                    stripped_line = line.strip()
                    if not stripped_line:
                        continue
                    rec = fallback_parser.parse_line(stripped_line)
                    if rec is None:
                        invalid_count += 1
                    else:
                        records.append(rec)
                    if len(records) >= max_records:
                        break
            if len(records) > 0:
                parser = fallback_parser
                detected_format = fallback_parser.FORMAT_NAME
                parser_name = fallback_parser.FORMAT_NAME

    valid_count = len(records)

    if not records:
        return {
            "status":           "error",
            "message":          "No valid records could be parsed from the file.",
            "detected_format":  detected_format,
            "parser_used":      parser_name,
            "parser_name":      parser_name,
            "total_lines":      total_lines,
            "valid_records":    0,
            "invalid_lines":    invalid_count,
            "invalid_records":  invalid_count,
            "available_fields": getattr(parser, "AVAILABLE_FIELDS", []) if parser else [],
            "records":          [],
            "sample_records":   [],
        }

    # 4. Build DataFrame
    df = pd.DataFrame(records)
    available_fields = list(df.columns)

    # 5. Clean
    raw_timestamp_series = None
    if "timestamp" in df.columns:
        raw_timestamp_series = df["timestamp"].astype(str)
        df["parsed_timestamp"] = _parse_timestamp_series(df["timestamp"])
    else:
        df["parsed_timestamp"] = pd.NaT

    if "port" in df.columns:
        df["port"] = pd.to_numeric(df["port"], errors="coerce").fillna(80).astype(int)
    else:
        df["port"] = 80

    if "ip" in df.columns:
        df["ip"] = df["ip"].astype(str).str.strip()
    else:
        df["ip"] = "127.0.0.1"

    if "path" not in df.columns:
        df["path"] = "/"
    else:
        df["path"] = df["path"].fillna("/").astype(str)

    if "method" not in df.columns:
        df["method"] = "GET"
    else:
        df["method"] = df["method"].fillna("GET").astype(str)

    if "status" not in df.columns:
        df["status"] = 200
    else:
        df["status"] = pd.to_numeric(df["status"], errors="coerce").fillna(200).astype(int)

    if "user_agent" in df.columns:
        df["user_agent"] = df["user_agent"].fillna("unknown").astype(str).str.strip()
    else:
        df["user_agent"] = "unknown"

    if "language" in df.columns:
        df["language"] = df["language"].fillna("unknown").astype(str).str.strip()
    if "metadata" in df.columns:
        df["metadata"] = df["metadata"].fillna("unknown").astype(str).str.strip()

    # 6. Security indicators
    ua_col = "user_agent"
    path_col = "path"
    if "scanner_type" not in df.columns:
        df["scanner_type"] = df.apply(lambda r: _detect_scanner(r[ua_col], r[path_col]), axis=1)
    if "bot_type" not in df.columns:
        df["bot_type"]     = df[ua_col].apply(_detect_bot)
    if "is_scanner" not in df.columns:
        df["is_scanner"]   = df["scanner_type"] != "none"
    if "is_bot" not in df.columns:
        df["is_bot"]       = df["bot_type"] != "none"
    if "is_browser" not in df.columns:
        df["is_browser"]   = df[ua_col].apply(_is_browser)
    if "user_agent_length" not in df.columns:
        df["user_agent_length"]  = df[ua_col].str.len().fillna(0).astype(int)
    if "user_agent_entropy" not in df.columns:
        df["user_agent_entropy"] = df[ua_col].apply(_string_entropy)

    # 7. IP-level features
    if df["parsed_timestamp"].notna().any():
        df = df.sort_values(["ip", "parsed_timestamp"]).reset_index(drop=True)
        df["requests_per_ip"]       = df.groupby("ip")["ip"].transform("count")
        df["unique_ports_per_ip"]   = df.groupby("ip")["port"].transform("nunique")
        df["time_between_requests"] = df.groupby("ip")["parsed_timestamp"].diff().dt.total_seconds()
        df["rapid_request_1s"]      = (df["time_between_requests"].fillna(999) <= 1)
        df["rapid_request_5s"]      = (df["time_between_requests"].fillna(999) <= 5)
    else:
        df["requests_per_ip"]       = df.groupby("ip")["ip"].transform("count")
        df["unique_ports_per_ip"]   = df.groupby("ip")["port"].transform("nunique")
        df["time_between_requests"] = 999.0
        df["rapid_request_1s"]      = False
        df["rapid_request_5s"]      = False

    # 8. Classification
    if "label" not in df.columns:
        df["label"] = df.apply(
            lambda r: _classify(
                r.get("scanner_type", "none"),
                r.get("bot_type", "none"),
                bool(r.get("rapid_request_1s", False)),
            ),
            axis=1,
        )

    # 9. Time features
    if df["parsed_timestamp"].notna().any():
        ts = df["parsed_timestamp"]
        df["hour"]        = ts.dt.hour.fillna(-1).astype(int)
        df["day_of_week"] = ts.dt.dayofweek.fillna(-1).astype(int)
        df["is_weekend"]  = df["day_of_week"] >= 5
    else:
        df["hour"]        = -1
        df["day_of_week"] = -1
        df["is_weekend"]  = False

    # 10. Risk score
    if "risk_score" not in df.columns:
        df["risk_score"] = df.apply(_compute_risk, axis=1)
    if "risk_level" not in df.columns:
        df["risk_level"] = df["risk_score"].apply(_risk_level)

    # Replace timestamp column with string representation for clean JSON output
    if raw_timestamp_series is not None:
        df["timestamp"] = raw_timestamp_series
    elif df["parsed_timestamp"].notna().any():
        df["timestamp"] = df["parsed_timestamp"].astype(str)

    # 11. Aggregations for dashboard
    label_counts = {str(k): int(v) for k, v in df["label"].value_counts().to_dict().items()}
    top_ips = []
    if "ip" in df.columns:
        top_ips = [
            {"ip": str(r["ip"]), "count": int(r["count"])}
            for r in (
                df.groupby("ip").size()
                .nlargest(10)
                .reset_index(name="count")
                .to_dict("records")
            )
        ]

    scanner_counts = {
        str(k): int(v)
        for k, v in df.loc[df["scanner_type"] != "none", "scanner_type"].value_counts().to_dict().items()
    }
    bot_counts = {
        str(k): int(v)
        for k, v in df.loc[df["bot_type"] != "none", "bot_type"].value_counts().to_dict().items()
    }

    # 12. Sample records for display (cleaned to strictly valid JSON types)
    display_cols = [c for c in df.columns if c != "parsed_timestamp"]
    sample_df = df[display_cols].head(100)
    sample_records = [_clean_record(row) for row in sample_df.to_dict("records")]

    # 13. Timestamp range
    ts_min = ts_max = None
    valid_ts = df["parsed_timestamp"].dropna()
    if not valid_ts.empty:
        ts_min = str(valid_ts.min())
        ts_max = str(valid_ts.max())

    avg_threat = round(float(df["risk_score"].mean()), 1) if not df.empty else 0.0

    return {
        "status":            "success",
        "detected_format":   detected_format,
        "parser_used":       parser_name,
        "parser_name":       parser_name,
        "total_lines":       int(total_lines),
        "valid_records":     int(valid_count),
        "invalid_lines":     int(invalid_count),
        "invalid_records":   int(invalid_count),
        "available_fields":  available_fields,
        "timestamp_min":     ts_min,
        "timestamp_max":     ts_max,
        "label_distribution": label_counts,
        "scanner_breakdown":  scanner_counts,
        "bot_breakdown":      bot_counts,
        "top_ips":            top_ips,
        "records":            sample_records,
        "sample_records":     sample_records,
        "unique_ips":         int(df["ip"].nunique()) if "ip" in df.columns else 0,
        "threat_score_avg":   avg_threat,
        "ml_prediction_available": False,
        "ml_note": (
            "ML prediction requires the same feature schema as the trained "
            "cj.log model. Upload a cj-format log for ML prediction."
            if detected_format != "cj"
            else "ML prediction available for this cj.log format."
        ),
    }
