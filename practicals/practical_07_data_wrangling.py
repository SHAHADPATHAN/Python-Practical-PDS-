"""
===========================================================================
PRACTICAL 7 - DATA WRANGLING
Python for Data Science
===========================================================================

Operations:
1. Group data by IP
2. Perform time-series resampling
3. Create pivot-table analysis
4. Filter bot/internal IP activity

Input:
    Data/processed/balanced_logs.csv

Outputs:
    Data/processed/ip_summary.csv
    Data/processed/hourly_activity.csv
    Data/processed/label_hour_pivot.csv
    Data/processed/filtered_activity.csv
    outputs/reports/practical_07_wrangling_report.txt
"""

from pathlib import Path
import ipaddress
import pandas as pd


# =========================================================================
# CONFIGURATION
# =========================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "Data" / "processed" / "balanced_logs.csv"

OUTPUT_DIR = BASE_DIR / "Data" / "processed"
REPORT_DIR = BASE_DIR / "outputs" / "reports"

IP_SUMMARY_FILE = OUTPUT_DIR / "ip_summary.csv"
HOURLY_FILE = OUTPUT_DIR / "hourly_activity.csv"
PIVOT_FILE = OUTPUT_DIR / "label_hour_pivot.csv"
FILTERED_FILE = OUTPUT_DIR / "filtered_activity.csv"

REPORT_FILE = REPORT_DIR / "practical_07_wrangling_report.txt"


# =========================================================================
# HELPER FUNCTIONS
# =========================================================================

def is_internal_ip(ip):
    """
    Identify private/internal IPv4 addresses.
    """
    try:
        return ipaddress.ip_address(str(ip)).is_private
    except ValueError:
        return False


def save_report(lines):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))


# =========================================================================
# MAIN
# =========================================================================

def main():

    print("=" * 75)
    print("PRACTICAL 7 - DATA WRANGLING")
    print("=" * 75)

    print(f"\nInput file: {INPUT_FILE}")

    if not INPUT_FILE.exists():
        print("ERROR: Input file not found.")
        return

    print("Input file status: FOUND")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # =====================================================================
    # LOAD DATA
    # =====================================================================

    print("\nLoading balanced dataset...")

    df = pd.read_csv(
        INPUT_FILE,
        parse_dates=["timestamp"]
    )

    print(f"Rows loaded    : {len(df):,}")
    print(f"Columns loaded : {len(df.columns)}")

    required_columns = [
        "timestamp",
        "ip",
        "label"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        print("\nERROR: Missing required columns:")
        print(missing_columns)
        return

    # =====================================================================
    # BASIC CLEANUP
    # =====================================================================

    print("\nPreparing data...")

    df = df.dropna(
        subset=["timestamp", "ip", "label"]
    ).copy()

    df["ip"] = df["ip"].astype(str).str.strip()
    df["label"] = df["label"].astype(str).str.strip().str.lower()

    df = df.sort_values(
        ["ip", "timestamp"]
    ).reset_index(drop=True)

    print(f"Rows after preparation: {len(df):,}")

    # =====================================================================
    # 1. GROUP BY IP
    # =====================================================================

    print("\n" + "=" * 75)
    print("1. IP-LEVEL GROUPING")
    print("=" * 75)

    ip_summary = (
        df.groupby("ip")
        .agg(
            total_requests=("ip", "size"),
            first_seen=("timestamp", "min"),
            last_seen=("timestamp", "max"),
            unique_labels=("label", "nunique"),
            scanner_requests=(
                "label",
                lambda x: (x == "scanner").sum()
            ),
            suspicious_requests=(
                "label",
                lambda x: (x == "suspicious").sum()
            ),
            benign_requests=(
                "label",
                lambda x: (x == "benign").sum()
            ),
            bot_requests=(
                "label",
                lambda x: (x == "bot").sum()
            )
        )
        .reset_index()
    )

    ip_summary["active_duration_seconds"] = (
        ip_summary["last_seen"]
        - ip_summary["first_seen"]
    ).dt.total_seconds()

    ip_summary = ip_summary.sort_values(
        "total_requests",
        ascending=False
    )

    ip_summary.to_csv(
        IP_SUMMARY_FILE,
        index=False
    )

    print(f"Unique IPs: {len(ip_summary):,}")

    print("\nTop 10 IPs by request count:")
    print(
        ip_summary[
            [
                "ip",
                "total_requests",
                "unique_labels",
                "scanner_requests",
                "suspicious_requests",
                "benign_requests",
                "bot_requests"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    # =====================================================================
    # 2. TIME-SERIES RESAMPLING
    # =====================================================================

    print("\n" + "=" * 75)
    print("2. TIME-SERIES RESAMPLING")
    print("=" * 75)

    time_df = df[
        ["timestamp", "label"]
    ].copy()

    time_df = time_df.set_index("timestamp")

    hourly_activity = (
        time_df
        .resample("1h")
        .size()
        .rename("request_count")
        .reset_index()
    )

    hourly_activity.to_csv(
        HOURLY_FILE,
        index=False
    )

    print(
        f"Hourly time-series rows: "
        f"{len(hourly_activity):,}"
    )

    print("\nFirst 10 hourly records:")
    print(
        hourly_activity
        .head(10)
        .to_string(index=False)
    )

    # =====================================================================
    # 3. PIVOT TABLE
    # =====================================================================

    print("\n" + "=" * 75)
    print("3. PIVOT TABLE")
    print("=" * 75)

    pivot_source = df[
        ["timestamp", "label"]
    ].copy()

    pivot_source["hour"] = (
        pivot_source["timestamp"]
        .dt.floor("1h")
    )

    label_hour_pivot = pd.pivot_table(
        pivot_source,
        index="hour",
        columns="label",
        values="timestamp",
        aggfunc="count",
        fill_value=0
    ).reset_index()

    label_hour_pivot.to_csv(
        PIVOT_FILE,
        index=False
    )

    print(
        f"Pivot-table rows: "
        f"{len(label_hour_pivot):,}"
    )

    print("\nPivot table sample:")
    print(
        label_hour_pivot
        .head(10)
        .to_string(index=False)
    )

    # =====================================================================
    # 4. FILTER BOT AND INTERNAL IP ACTIVITY
    # =====================================================================

    print("\n" + "=" * 75)
    print("4. BOT / INTERNAL IP FILTERING")
    print("=" * 75)

    df["is_internal_ip"] = df["ip"].apply(
        is_internal_ip
    )

    bot_records = df[
        df["label"] == "bot"
    ].copy()

    internal_records = df[
        df["is_internal_ip"]
    ].copy()

    # Combine bot and internal activity
    filtered_activity = df[
        (df["label"] == "bot") |
        (df["is_internal_ip"])
    ].copy()

    filtered_activity.to_csv(
        FILTERED_FILE,
        index=False
    )

    print(f"Bot records             : {len(bot_records):,}")
    print(f"Internal IP records     : {len(internal_records):,}")
    print(
        f"Bot/internal combined   : "
        f"{len(filtered_activity):,}"
    )

    # =====================================================================
    # VERIFICATION
    # =====================================================================

    print("\n" + "=" * 75)
    print("OUTPUT VERIFICATION")
    print("=" * 75)

    output_files = [
        IP_SUMMARY_FILE,
        HOURLY_FILE,
        PIVOT_FILE,
        FILTERED_FILE
    ]

    for output_file in output_files:

        if output_file.exists():

            size_mb = (
                output_file.stat().st_size
                / (1024 * 1024)
            )

            print(
                f"{output_file.name:<30} "
                f"{size_mb:>8.2f} MB"
            )

        else:
            print(
                f"{output_file.name:<30} "
                f"NOT FOUND"
            )

    # =====================================================================
    # REPORT
    # =====================================================================

    report = []

    report.append("=" * 75)
    report.append("PRACTICAL 7 - DATA WRANGLING REPORT")
    report.append("=" * 75)
    report.append("")

    report.append("INPUT DATASET")
    report.append("-" * 75)
    report.append(f"Input file: {INPUT_FILE}")
    report.append(f"Rows processed: {len(df):,}")
    report.append(f"Columns processed: {len(df.columns):,}")
    report.append("")

    report.append("1. IP-LEVEL GROUPING")
    report.append("-" * 75)
    report.append(
        f"Unique IP addresses: {len(ip_summary):,}"
    )
    report.append(
        f"IP summary output: {IP_SUMMARY_FILE}"
    )
    report.append("")

    report.append("2. TIME-SERIES RESAMPLING")
    report.append("-" * 75)
    report.append(
        f"Hourly records: {len(hourly_activity):,}"
    )
    report.append(
        f"Hourly output: {HOURLY_FILE}"
    )
    report.append("")

    report.append("3. PIVOT TABLE")
    report.append("-" * 75)
    report.append(
        f"Pivot rows: {len(label_hour_pivot):,}"
    )
    report.append(
        f"Pivot output: {PIVOT_FILE}"
    )
    report.append("")

    report.append("4. BOT / INTERNAL IP FILTERING")
    report.append("-" * 75)
    report.append(
        f"Bot records: {len(bot_records):,}"
    )
    report.append(
        f"Internal IP records: {len(internal_records):,}"
    )
    report.append(
        f"Combined filtered records: "
        f"{len(filtered_activity):,}"
    )
    report.append(
        f"Filtered output: {FILTERED_FILE}"
    )
    report.append("")

    report.append("OBSERVATION")
    report.append("-" * 75)
    report.append(
        "The balanced log dataset was transformed into "
        "IP-level summaries, hourly time-series data, "
        "label-based pivot data, and filtered bot/internal "
        "IP activity."
    )

    save_report(report)

    print("\nReport saved to:")
    print(REPORT_FILE)

    print("\n" + "=" * 75)
    print("PRACTICAL 7 COMPLETED SUCCESSFULLY")
    print("=" * 75)


if __name__ == "__main__":
    main()