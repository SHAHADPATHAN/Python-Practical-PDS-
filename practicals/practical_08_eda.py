"""
===========================================================================
PRACTICAL 8 - VISUALIZATION & EXPLORATORY DATA ANALYSIS
Python for Data Science
===========================================================================

Purpose:
    Perform EDA and create visualizations from the balanced web-log data.

Input:
    Data/processed/balanced_logs.csv

Outputs:
    outputs/figures/*.png
    outputs/reports/practical_08_eda_report.txt

Important source limitation:
    The original cj.log does not contain an HTTP status-code field.
    Therefore, status-code visualization is not fabricated.
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# =========================================================================
# CONFIGURATION
# =========================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "Data" / "processed" / "balanced_logs.csv"

FIGURE_DIR = BASE_DIR / "outputs" / "figures"
REPORT_DIR = BASE_DIR / "outputs" / "reports"

REPORT_FILE = REPORT_DIR / "practical_08_eda_report.txt"


# =========================================================================
# SETUP
# =========================================================================

FIGURE_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")


def save_figure(filename):
    """
    Save the current Matplotlib figure.
    """
    output_file = FIGURE_DIR / filename

    plt.tight_layout()
    plt.savefig(
        output_file,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    return output_file


# =========================================================================
# MAIN
# =========================================================================

def main():

    print("=" * 75)
    print("PRACTICAL 8 - VISUALIZATION & EDA")
    print("=" * 75)

    print(f"\nInput file: {INPUT_FILE}")

    if not INPUT_FILE.exists():
        print("ERROR: Input file not found.")
        return

    print("Input file status: FOUND")

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
        print("\nERROR: Required columns missing:")
        print(missing_columns)
        return

    # =====================================================================
    # BASIC PREPARATION
    # =====================================================================

    print("\nPreparing data...")

    df = df.dropna(
        subset=["timestamp", "ip", "label"]
    ).copy()

    df["label"] = (
        df["label"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["ip"] = (
        df["ip"]
        .astype(str)
        .str.strip()
    )

    df = df.sort_values("timestamp")

    # Create useful time columns
    df["date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.floor("1D")
    df["hour_timestamp"] = df["timestamp"].dt.floor("1h")

    print(f"Rows after preparation: {len(df):,}")

    # =====================================================================
    # REPORT DATA
    # =====================================================================

    report = []

    report.append("=" * 75)
    report.append("PRACTICAL 8 - VISUALIZATION & EDA REPORT")
    report.append("=" * 75)
    report.append("")

    report.append("DATASET")
    report.append("-" * 75)
    report.append(f"Input file: {INPUT_FILE}")
    report.append(f"Rows analyzed: {len(df):,}")
    report.append(f"Columns analyzed: {len(df.columns):,}")
    report.append("")

    # =====================================================================
    # 1. LABEL DISTRIBUTION
    # =====================================================================

    print("\n" + "=" * 75)
    print("1. LABEL DISTRIBUTION")
    print("=" * 75)

    label_counts = (
        df["label"]
        .value_counts()
        .sort_values(ascending=False)
    )

    print(label_counts.to_string())

    plt.figure(figsize=(9, 6))

    sns.barplot(
        x=label_counts.index,
        y=label_counts.values
    )

    plt.title("Log Activity Distribution by Label")
    plt.xlabel("Label")
    plt.ylabel("Number of Records")

    output = save_figure(
        "01_label_distribution.png"
    )

    print(f"\nFigure saved: {output}")

    report.append("1. LABEL DISTRIBUTION")
    report.append("-" * 75)

    for label, count in label_counts.items():

        percentage = (
            count / len(df)
        ) * 100

        report.append(
            f"{label:<15} "
            f"{count:>8,} "
            f"({percentage:.2f}%)"
        )

    report.append("")

    # =====================================================================
    # 2. REQUESTS OVER TIME
    # =====================================================================

    print("\n" + "=" * 75)
    print("2. REQUESTS OVER TIME")
    print("=" * 75)

    daily_requests = (
        df.set_index("timestamp")
        .resample("1D")
        .size()
    )

    print(
        f"Number of daily time points: "
        f"{len(daily_requests):,}"
    )

    plt.figure(figsize=(14, 6))

    plt.plot(
        daily_requests.index,
        daily_requests.values
    )

    plt.title("Requests Over Time")
    plt.xlabel("Date")
    plt.ylabel("Number of Requests")

    output = save_figure(
        "02_requests_over_time.png"
    )

    print(f"Figure saved: {output}")

    report.append("2. REQUESTS OVER TIME")
    report.append("-" * 75)
    report.append(
        f"Daily time points: {len(daily_requests):,}"
    )

    if len(daily_requests) > 0:

        peak_date = daily_requests.idxmax()
        peak_count = daily_requests.max()

        report.append(
            f"Peak date: {peak_date.date()}"
        )

        report.append(
            f"Peak daily requests: {peak_count:,}"
        )

    report.append("")

    # =====================================================================
    # 3. REQUESTS BY HOUR
    # =====================================================================

    print("\n" + "=" * 75)
    print("3. REQUESTS BY HOUR")
    print("=" * 75)

    hourly_requests = (
        df["hour"]
        .value_counts()
        .sort_index()
    )

    print(hourly_requests.to_string())

    plt.figure(figsize=(12, 6))

    sns.barplot(
        x=hourly_requests.index,
        y=hourly_requests.values
    )

    plt.title("Requests by Hour of Day")
    plt.xlabel("Hour")
    plt.ylabel("Number of Requests")

    output = save_figure(
        "03_requests_by_hour.png"
    )

    print(f"\nFigure saved: {output}")

    report.append("3. REQUESTS BY HOUR")
    report.append("-" * 75)

    for hour, count in hourly_requests.items():

        report.append(
            f"{int(hour):02d}:00 - {count:,} requests"
        )

    report.append("")

    # =====================================================================
    # 4. TOP 10 IPs
    # =====================================================================

    print("\n" + "=" * 75)
    print("4. TOP 10 IPs BY REQUEST COUNT")
    print("=" * 75)

    top_ips = (
        df["ip"]
        .value_counts()
        .head(10)
        .sort_values(ascending=True)
    )

    print(
        top_ips.sort_values(
            ascending=False
        ).to_string()
    )

    plt.figure(figsize=(11, 7))

    sns.barplot(
        x=top_ips.values,
        y=top_ips.index
    )

    plt.title("Top 10 IP Addresses by Request Count")
    plt.xlabel("Number of Requests")
    plt.ylabel("IP Address")

    output = save_figure(
        "04_top_10_ips.png"
    )

    print(f"\nFigure saved: {output}")

    report.append("4. TOP 10 IPs")
    report.append("-" * 75)

    for ip, count in top_ips.sort_values(
        ascending=False
    ).items():

        report.append(
            f"{ip:<20} {count:,}"
        )

    report.append("")

    # =====================================================================
    # 5. LABEL ACTIVITY OVER TIME
    # =====================================================================

    print("\n" + "=" * 75)
    print("5. LABEL ACTIVITY OVER TIME")
    print("=" * 75)

    label_time = (
        df.groupby(
            ["hour_timestamp", "label"]
        )
        .size()
        .unstack(fill_value=0)
    )

    print(
        f"Time points analyzed: "
        f"{len(label_time):,}"
    )

    plt.figure(figsize=(15, 7))

    for label in label_time.columns:

        plt.plot(
            label_time.index,
            label_time[label],
            label=label
        )

    plt.title("Log Activity Categories Over Time")
    plt.xlabel("Time")
    plt.ylabel("Number of Requests")
    plt.legend()

    output = save_figure(
        "05_labels_over_time.png"
    )

    print(f"Figure saved: {output}")

    report.append("5. LABEL ACTIVITY OVER TIME")
    report.append("-" * 75)
    report.append(
        f"Hourly time points: {len(label_time):,}"
    )
    report.append("")

    # =====================================================================
    # 6. HOURLY LABEL HEATMAP
    # =====================================================================

    print("\n" + "=" * 75)
    print("6. HOURLY LABEL HEATMAP")
    print("=" * 75)

    heatmap_data = pd.crosstab(
        df["hour"],
        df["label"]
    )

    print("\nHeatmap data:")
    print(heatmap_data.to_string())

    plt.figure(figsize=(10, 8))

    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt="d"
    )

    plt.title("Hourly Log Activity by Label")
    plt.xlabel("Label")
    plt.ylabel("Hour of Day")

    output = save_figure(
        "06_hourly_label_heatmap.png"
    )

    print(f"\nFigure saved: {output}")

    report.append("6. HOURLY LABEL HEATMAP")
    report.append("-" * 75)

    report.append(
        heatmap_data.to_string()
    )

    report.append("")

    # =====================================================================
    # 7. TOP SCANNER IPS
    # =====================================================================

    print("\n" + "=" * 75)
    print("7. TOP SCANNER IPS")
    print("=" * 75)

    scanner_df = df[
        df["label"] == "scanner"
    ]

    top_scanner_ips = (
        scanner_df["ip"]
        .value_counts()
        .head(10)
        .sort_values(ascending=True)
    )

    print(
        top_scanner_ips
        .sort_values(ascending=False)
        .to_string()
    )

    plt.figure(figsize=(11, 7))

    sns.barplot(
        x=top_scanner_ips.values,
        y=top_scanner_ips.index
    )

    plt.title("Top 10 Scanner IP Addresses")
    plt.xlabel("Scanner Requests")
    plt.ylabel("IP Address")

    output = save_figure(
        "07_top_scanner_ips.png"
    )

    print(f"\nFigure saved: {output}")

    report.append("7. TOP SCANNER IPs")
    report.append("-" * 75)

    for ip, count in top_scanner_ips.sort_values(
        ascending=False
    ).items():

        report.append(
            f"{ip:<20} {count:,}"
        )

    report.append("")

    # =====================================================================
    # 8. BOT VS INTERNAL ACTIVITY
    # =====================================================================

    print("\n" + "=" * 75)
    print("8. BOT / INTERNAL ACTIVITY")
    print("=" * 75)

    if "is_internal_ip" not in df.columns:

        import ipaddress

        def check_internal(ip):

            try:
                return ipaddress.ip_address(
                    str(ip)
                ).is_private

            except ValueError:
                return False

        df["is_internal_ip"] = (
            df["ip"]
            .apply(check_internal)
        )

    bot_count = (
        df["label"] == "bot"
    ).sum()

    internal_count = (
        df["is_internal_ip"]
    ).sum()

    activity_counts = pd.Series(
        {
            "Bot": bot_count,
            "Internal IP": internal_count
        }
    )

    print(activity_counts.to_string())

    plt.figure(figsize=(8, 6))

    sns.barplot(
        x=activity_counts.index,
        y=activity_counts.values
    )

    plt.title("Bot and Internal IP Activity")
    plt.xlabel("Activity Type")
    plt.ylabel("Number of Records")

    output = save_figure(
        "08_bot_internal_activity.png"
    )

    print(f"\nFigure saved: {output}")

    report.append("8. BOT / INTERNAL ACTIVITY")
    report.append("-" * 75)
    report.append(
        f"Bot records: {bot_count:,}"
    )
    report.append(
        f"Internal IP records: {internal_count:,}"
    )
    report.append("")

    # =====================================================================
    # STATUS CODE LIMITATION
    # =====================================================================

    print("\n" + "=" * 75)
    print("STATUS CODE ANALYSIS")
    print("=" * 75)

    status_available = "status" in df.columns

    if status_available:

        print("Status-code field FOUND.")

        status_counts = (
            df["status"]
            .value_counts()
            .sort_index()
        )

        print(status_counts.to_string())

        plt.figure(figsize=(10, 6))

        sns.barplot(
            x=status_counts.index.astype(str),
            y=status_counts.values
        )

        plt.title("HTTP Status Code Distribution")
        plt.xlabel("HTTP Status Code")
        plt.ylabel("Number of Requests")

        output = save_figure(
            "09_status_code_distribution.png"
        )

        print(f"Figure saved: {output}")

        report.append(
            "9. HTTP STATUS CODE DISTRIBUTION"
        )
        report.append("-" * 75)
        report.append(
            status_counts.to_string()
        )

    else:

        print(
            "Status-code field NOT available "
            "in the original cj.log dataset."
        )

        print(
            "Status-code visualization was therefore "
            "not fabricated."
        )

        report.append(
            "9. HTTP STATUS CODE DISTRIBUTION"
        )
        report.append("-" * 75)
        report.append(
            "Not available: cj.log does not contain "
            "an HTTP status-code field."
        )

    report.append("")

    # =====================================================================
    # GENERAL OBSERVATIONS
    # =====================================================================

    report.append("GENERAL EDA OBSERVATIONS")
    report.append("-" * 75)

    report.append(
        "1. The balanced dataset contains equal representation "
        "of scanner, suspicious, benign and bot labels."
    )

    report.append(
        "2. IP-level analysis identifies high-volume sources "
        "and their associated activity labels."
    )

    report.append(
        "3. Time-based analysis shows how request activity "
        "changes across dates and hours."
    )

    report.append(
        "4. The heatmap provides a compact view of activity "
        "by hour and label."
    )

    report.append(
        "5. HTTP status-code analysis cannot be performed "
        "because the source log does not contain a status field."
    )

    report.append("")

    # =====================================================================
    # SAVE REPORT
    # =====================================================================

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "\n".join(report)
        )

    # =====================================================================
    # FINAL OUTPUT
    # =====================================================================

    print("\n" + "=" * 75)
    print("EDA OUTPUT FILES")
    print("=" * 75)

    for file in sorted(FIGURE_DIR.glob("*.png")):

        size_mb = (
            file.stat().st_size
            / (1024 * 1024)
        )

        print(
            f"{file.name:<40} "
            f"{size_mb:.2f} MB"
        )

    print("\nReport saved to:")
    print(REPORT_FILE)

    print("\n" + "=" * 75)
    print("PRACTICAL 8 COMPLETED SUCCESSFULLY")
    print("=" * 75)


# =========================================================================
# ENTRY POINT
# =========================================================================

if __name__ == "__main__":
    main()