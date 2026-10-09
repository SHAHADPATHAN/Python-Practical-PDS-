"""
Dataset summary service.
Reads from pre-generated reports and small CSVs — never loads the
full 700+ MB feature dataset into memory.
"""

import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from backend.utils import cache, paths


# ─── Hard-coded ground-truth facts from the completed practicals ──────────────
# These numbers come directly from practical_04_labeling_report.txt and
# practical_06_balancing_report.txt.  They are NOT fabricated.

DATASET_FACTS: Dict[str, Any] = {
    "source_file":       "cj.log",
    "file_size_mb":      215.4,
    "total_lines":       2_061_431,
    "valid_records":     2_060_520,
    "invalid_json":      911,
    "fields": [
        "timestamp", "ip", "port",
        "user_agent", "language", "metadata",
    ],
    "label_distribution": {
        "scanner":    1_827_367,
        "suspicious":   167_486,
        "benign":        61_091,
        "bot":            4_576,
    },
    "scanner_breakdown": {
        "gobuster":   1_408_510,
        "dirbuster":    397_212,
        "nmap":           9_204,
        "nikto":          7_044,
        "zgrab":          4_219,
        "nessus":           718,
        "masscan":          437,
        "wpscan":            23,
    },
    "bot_breakdown": {
        "python-requests": 2_276,
        "go-http-client":  2_166,
        "bot":               106,
        "spider":             15,
        "curl/":               8,
        "crawler":             5,
    },
    "rapid_requests_1s": 1_991_414,
    # balanced dataset used for ML
    "balanced_rows":   18_304,
    "balanced_per_class": 4_576,
    # ML results
    "ml_accuracy":    0.9921,
    "ml_precision":   0.9923,
    "ml_recall":      0.9921,
    "ml_f1":          0.9921,
    "ml_train_rows":  14_643,
    "ml_test_rows":    3_661,
    "ml_feature_count": 9450,
    # Practical completions
    "practicals_completed": 10,
}


def get_dataset_summary() -> Dict[str, Any]:
    """Return high-level summary dict (cached after first call)."""
    if cache.has("dataset_summary"):
        return cache.get("dataset_summary")

    summary = dict(DATASET_FACTS)

    # Augment with live file-existence checks
    summary["files"] = {
        "structured_csv":    paths.STRUCTURED_CSV.exists(),
        "cleaned_csv":       paths.CLEANED_CSV.exists(),
        "labeled_csv":       paths.LABELED_CSV.exists(),
        "features_csv":      paths.FEATURES_CSV.exists(),
        "balanced_csv":      paths.BALANCED_CSV.exists(),
        "ip_summary_csv":    paths.IP_SUMMARY_CSV.exists(),
        "hourly_csv":        paths.HOURLY_CSV.exists(),
        "pivot_csv":         paths.PIVOT_CSV.exists(),
        "model_file":        paths.MODEL_FILE.exists(),
    }

    # Read ip_summary.csv to get unique IP count (only ~243 KB)
    if paths.IP_SUMMARY_CSV.exists():
        try:
            ip_df = pd.read_csv(paths.IP_SUMMARY_CSV, usecols=["ip"])
            summary["unique_ips"] = int(len(ip_df))
        except Exception:
            summary["unique_ips"] = None
    else:
        summary["unique_ips"] = None

    cache.set("dataset_summary", summary)
    return summary


def get_label_distribution() -> Dict[str, Any]:
    """Return label counts and percentages."""
    if cache.has("label_distribution"):
        return cache.get("label_distribution")

    labels = DATASET_FACTS["label_distribution"]
    total  = sum(labels.values())
    result = {
        "total": total,
        "labels": [
            {
                "label":      label,
                "count":      count,
                "percentage": round(count / total * 100, 2),
            }
            for label, count in sorted(
                labels.items(), key=lambda x: x[1], reverse=True
            )
        ],
    }
    cache.set("label_distribution", result)
    return result


def get_scanner_breakdown() -> Dict[str, Any]:
    """Return scanner tool breakdown."""
    if cache.has("scanner_breakdown"):
        return cache.get("scanner_breakdown")

    scanners  = DATASET_FACTS["scanner_breakdown"]
    total_s   = sum(scanners.values())
    total_all = DATASET_FACTS["valid_records"]

    result = {
        "total_scanner_records": DATASET_FACTS["label_distribution"]["scanner"],
        "tools": [
            {
                "tool":       tool,
                "records":    count,
                "percentage_of_scanners": round(count / total_s * 100, 2)
                    if total_s else 0,
                "percentage_of_dataset":  round(count / total_all * 100, 4)
                    if total_all else 0,
            }
            for tool, count in sorted(
                scanners.items(), key=lambda x: x[1], reverse=True
            )
        ],
    }
    cache.set("scanner_breakdown", result)
    return result
