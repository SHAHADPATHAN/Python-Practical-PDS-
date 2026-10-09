"""
Practical 5: Feature Engineering

Input:
    Data/processed/labeled_logs.csv

Output:
    Data/processed/features.csv

Objective:
    Create meaningful numerical and categorical features
    for anomaly detection and machine learning.
"""

from pathlib import Path
import math
import re

import pandas as pd


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "Data"
    / "processed"
    / "labeled_logs.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "Data"
    / "processed"
    / "features.csv"
)

REPORT_DIR = (
    BASE_DIR
    / "outputs"
    / "reports"
)

REPORT_FILE = (
    REPORT_DIR
    / "practical_05_feature_report.txt"
)


# ============================================================
# 2. SETTINGS
# ============================================================

CHUNK_SIZE = 50_000


# ============================================================
# 3. CHECK INPUT
# ============================================================

print("=" * 75)
print("PRACTICAL 5 - FEATURE ENGINEERING")
print("=" * 75)

print(f"\nInput file: {INPUT_FILE}")

if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"Input file not found:\n{INPUT_FILE}"
    )

print("Input file status: FOUND")


# ============================================================
# 4. HELPER FUNCTIONS
# ============================================================

def string_entropy(value):
    """
    Calculate Shannon entropy of a string.

    Higher entropy can indicate more randomness.
    """

    if pd.isna(value):

        return 0.0

    value = str(value)

    if not value:

        return 0.0

    counts = {}

    for character in value:

        counts[character] = (
            counts.get(character, 0) + 1
        )

    length = len(value)

    entropy = 0.0

    for count in counts.values():

        probability = count / length

        entropy -= (
            probability
            * math.log2(probability)
        )

    return entropy


def detect_scanner(user_agent):
    """
    Identify known scanner/security tools.
    """

    if pd.isna(user_agent):

        return "none"

    text = str(user_agent).lower()

    scanner_patterns = {
        "gobuster": "gobuster",
        "dirbuster": "dirbuster",
        "nmap": "nmap",
        "nikto": "nikto",
        "zgrab": "zgrab",
        "nessus": "nessus",
        "masscan": "masscan",
        "wpscan": "wpscan",
        "sqlmap": "sqlmap",
        "burp": "burp",
        "nuclei": "nuclei",
        "acunetix": "acunetix",
        "openvas": "openvas"
    }

    for pattern, name in scanner_patterns.items():

        if pattern in text:

            return name

    return "none"


def detect_bot(user_agent):
    """
    Identify common automated clients.
    """

    if pd.isna(user_agent):

        return "none"

    text = str(user_agent).lower()

    bot_patterns = {
        "python-requests": "python-requests",
        "go-http-client": "go-http-client",
        "crawler": "crawler",
        "spider": "spider",
        "bot": "bot",
        "scrapy": "scrapy",
        "curl/": "curl",
        "wget/": "wget",
        "urllib": "urllib"
    }

    for pattern, name in bot_patterns.items():

        if pattern in text:

            return name

    return "none"


def detect_browser(user_agent):
    """
    Detect common browser user-agents.
    """

    if pd.isna(user_agent):

        return False

    text = str(user_agent).lower()

    browser_patterns = [
        "mozilla",
        "chrome",
        "firefox",
        "safari",
        "edge",
        "opera"
    ]

    return any(
        pattern in text
        for pattern in browser_patterns
    )


# ============================================================
# 5. LOAD DATA
# ============================================================

print("\nLoading labeled dataset...")

df = pd.read_csv(
    INPUT_FILE,
    parse_dates=["timestamp"]
)

print(
    f"Rows loaded: {len(df):,}"
)

print(
    f"Columns loaded: {len(df.columns)}"
)


# ============================================================
# 6. BASIC SORTING
# ============================================================

print("\nSorting records by IP and timestamp...")

df = df.sort_values(
    ["ip", "timestamp"]
).reset_index(
    drop=True
)


# ============================================================
# 7. GLOBAL IP-LEVEL FEATURES
# ============================================================

print("\nCreating IP-level features...")


# Total requests from each IP

df["requests_per_ip"] = (
    df.groupby("ip")["ip"]
    .transform("count")
)


# Unique ports used by each IP

df["unique_ports_per_ip"] = (
    df.groupby("ip")["port"]
    .transform("nunique")
)


# First time the IP appeared

df["ip_first_seen"] = (
    df.groupby("ip")["timestamp"]
    .transform("min")
)


# Last time the IP appeared

df["ip_last_seen"] = (
    df.groupby("ip")["timestamp"]
    .transform("max")
)


# Active duration of IP in seconds

df["ip_active_duration_seconds"] = (
    df["ip_last_seen"]
    - df["ip_first_seen"]
).dt.total_seconds()


# ============================================================
# 8. TIME BETWEEN REQUESTS
# ============================================================

print("Creating time-based features...")


df["time_between_requests"] = (
    df.groupby("ip")["timestamp"]
    .diff()
    .dt.total_seconds()
)


# Replace negative differences caused by timestamp anomalies

df.loc[
    df["time_between_requests"] < 0,
    "time_between_requests"
] = pd.NA


# Rapid request indicators

df["rapid_request_1s"] = (
    df["time_between_requests"]
    .notna()
    &
    (
        df["time_between_requests"] <= 1
    )
)


df["rapid_request_5s"] = (
    df["time_between_requests"]
    .notna()
    &
    (
        df["time_between_requests"] <= 5
    )
)


# ============================================================
# 9. REQUEST RATE FEATURES
# ============================================================

print("Creating request-rate features...")


# Requests per minute for each IP

df["request_minute"] = (
    df["timestamp"]
    .dt.floor("min")
)


df["requests_per_ip_minute"] = (
    df.groupby(
        ["ip", "request_minute"]
    )["ip"]
    .transform("count")
)


# Requests per hour

df["request_hour"] = (
    df["timestamp"]
    .dt.floor("h")
)


df["requests_per_ip_hour"] = (
    df.groupby(
        ["ip", "request_hour"]
    )["ip"]
    .transform("count")
)


# ============================================================
# 10. USER-AGENT FEATURES
# ============================================================

print("Creating User-Agent features...")


df["scanner_type"] = (
    df["user_agent"]
    .apply(detect_scanner)
)


df["bot_type"] = (
    df["user_agent"]
    .apply(detect_bot)
)


df["is_scanner"] = (
    df["scanner_type"] != "none"
)


df["is_bot"] = (
    df["bot_type"] != "none"
)


df["is_browser"] = (
    df["user_agent"]
    .apply(detect_browser)
)


df["user_agent_length"] = (
    df["user_agent"]
    .astype("string")
    .str.len()
)


df["user_agent_entropy"] = (
    df["user_agent"]
    .apply(string_entropy)
)


# ============================================================
# 11. METADATA FEATURES
# ============================================================

print("Creating metadata features...")


df["metadata_present"] = (
    df["metadata"]
    .notna()
    &
    (
        df["metadata"]
        .astype(str)
        .str.lower()
        != "unknown"
    )
)


df["metadata_length"] = (
    df["metadata"]
    .astype("string")
    .str.len()
)


df["metadata_entropy"] = (
    df["metadata"]
    .apply(string_entropy)
)


# ============================================================
# 12. LANGUAGE FEATURES
# ============================================================

print("Creating language features...")


df["language_present"] = (
    df["language"]
    .notna()
    &
    (
        df["language"]
        .astype(str)
        .str.lower()
        != "unknown"
    )
)


df["language_length"] = (
    df["language"]
    .astype("string")
    .str.len()
)


# ============================================================
# 13. TIME FEATURES
# ============================================================

print("Creating calendar/time features...")


df["year"] = (
    df["timestamp"].dt.year
)

df["month"] = (
    df["timestamp"].dt.month
)

df["day"] = (
    df["timestamp"].dt.day
)

df["hour"] = (
    df["timestamp"].dt.hour
)

df["day_of_week"] = (
    df["timestamp"].dt.dayofweek
)

df["is_weekend"] = (
    df["day_of_week"] >= 5
)


# ============================================================
# 14. PORT FEATURES
# ============================================================

print("Creating port features...")


df["is_low_port"] = (
    df["port"] < 1024
)


df["is_ephemeral_port"] = (
    df["port"] >= 1024
)


# ============================================================
# 15. IP BEHAVIOR FEATURES
# ============================================================

print("Creating IP behavior features...")


df["high_volume_ip"] = (
    df["requests_per_ip"] >= 1000
)


df["very_high_volume_ip"] = (
    df["requests_per_ip"] >= 10000
)


# ============================================================
# 16. COMBINATION / RISK FEATURES
# ============================================================

print("Creating combined behavioral features...")


df["scanner_and_high_volume"] = (
    df["is_scanner"]
    &
    df["high_volume_ip"]
)


df["rapid_and_high_volume"] = (
    df["rapid_request_1s"]
    &
    df["high_volume_ip"]
)


df["automated_activity"] = (
    df["is_scanner"]
    |
    df["is_bot"]
)


# ============================================================
# 17. REMOVE TEMPORARY GROUPING COLUMNS
# ============================================================

df.drop(
    columns=[
        "request_minute",
        "request_hour"
    ],
    inplace=True
)


# ============================================================
# 18. SAVE FEATURE DATASET
# ============================================================

print("\nSaving feature dataset...")

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 19. FEATURE LIST
# ============================================================

feature_columns = [
    "requests_per_ip",
    "unique_ports_per_ip",
    "ip_active_duration_seconds",
    "time_between_requests",
    "rapid_request_1s",
    "rapid_request_5s",
    "requests_per_ip_minute",
    "requests_per_ip_hour",
    "scanner_type",
    "bot_type",
    "is_scanner",
    "is_bot",
    "is_browser",
    "user_agent_length",
    "user_agent_entropy",
    "metadata_present",
    "metadata_length",
    "metadata_entropy",
    "language_present",
    "language_length",
    "year",
    "month",
    "day",
    "hour",
    "day_of_week",
    "is_weekend",
    "is_low_port",
    "is_ephemeral_port",
    "high_volume_ip",
    "very_high_volume_ip",
    "scanner_and_high_volume",
    "rapid_and_high_volume",
    "automated_activity"
]


# ============================================================
# 20. OUTPUT VERIFICATION
# ============================================================

print("\n" + "-" * 75)
print("FEATURE DATASET VERIFICATION")
print("-" * 75)

output_size_mb = (
    OUTPUT_FILE.stat().st_size
    / (1024 * 1024)
)

print(
    f"Output file : {OUTPUT_FILE}"
)

print(
    f"Output size : {output_size_mb:.2f} MB"
)

print(
    f"Rows        : {len(df):,}"
)

print(
    f"Columns     : {len(df.columns)}"
)


# ============================================================
# 21. FEATURE SUMMARY
# ============================================================

print("\n" + "-" * 75)
print("ENGINEERED FEATURES")
print("-" * 75)

for number, feature in enumerate(
    feature_columns,
    start=1
):

    print(
        f"{number:>2}. {feature}"
    )


# ============================================================
# 22. NUMERICAL FEATURE SUMMARY
# ============================================================

print("\n" + "-" * 75)
print("NUMERICAL FEATURE SUMMARY")
print("-" * 75)

numeric_features = [
    feature
    for feature in feature_columns
    if feature in df.columns
    and pd.api.types.is_numeric_dtype(
        df[feature]
    )
]

print(
    df[numeric_features]
    .describe()
    .T
    .to_string()
)


# ============================================================
# 23. LABEL + FEATURE ANALYSIS
# ============================================================

print("\n" + "-" * 75)
print("LABEL DISTRIBUTION")
print("-" * 75)

print(
    df["label"]
    .value_counts()
    .to_string()
)


# ============================================================
# 24. TOP IPs
# ============================================================

print("\n" + "-" * 75)
print("TOP 10 IPs BY REQUEST COUNT")
print("-" * 75)

top_ips = (
    df.groupby("ip")
    .size()
    .sort_values(
        ascending=False
    )
    .head(10)
)

print(top_ips.to_string())


# ============================================================
# 25. FEATURE DATA SAMPLE
# ============================================================

print("\n" + "-" * 75)
print("FEATURE DATA SAMPLE")
print("-" * 75)

sample_columns = [
    "timestamp",
    "ip",
    "label",
    "requests_per_ip",
    "unique_ports_per_ip",
    "time_between_requests",
    "requests_per_ip_minute",
    "requests_per_ip_hour",
    "scanner_type",
    "bot_type",
    "is_scanner",
    "is_bot",
    "is_browser",
    "user_agent_length",
    "metadata_present",
    "high_volume_ip",
    "automated_activity"
]

print(
    df[sample_columns]
    .head(15)
    .to_string(index=False)
)


# ============================================================
# 26. SAVE REPORT
# ============================================================

with REPORT_FILE.open(
    "w",
    encoding="utf-8"
) as report:

    report.write(
        "PRACTICAL 5 - FEATURE ENGINEERING REPORT\n"
    )

    report.write(
        "=" * 60 + "\n\n"
    )

    report.write(
        f"Input file: {INPUT_FILE}\n"
    )

    report.write(
        f"Output file: {OUTPUT_FILE}\n\n"
    )

    report.write(
        f"Rows: {len(df):,}\n"
    )

    report.write(
        f"Columns: {len(df.columns)}\n\n"
    )

    report.write(
        "ENGINEERED FEATURES\n"
    )

    for feature in feature_columns:

        report.write(
            f"- {feature}\n"
        )

    report.write(
        "\nSOURCE-DATA LIMITATIONS\n"
    )

    report.write(
        "- HTTP status code is not present in the "
        "source dataset, so status-code frequency "
        "was not created.\n"
    )

    report.write(
        "- HTTP request URL/path is not present in "
        "the source dataset, so URL entropy was not "
        "created from a request path.\n"
    )

    report.write(
        "- User-Agent and metadata entropy were "
        "created as available string-entropy features.\n"
    )


# ============================================================
# 27. COMPLETION
# ============================================================

print("\nReport saved to:")
print(REPORT_FILE)

print("\n" + "=" * 75)
print("PRACTICAL 5 COMPLETED SUCCESSFULLY")
print("=" * 75)