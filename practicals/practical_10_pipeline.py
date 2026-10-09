"""
===========================================================================
PRACTICAL 10 - REUSABLE DATA SCIENCE PIPELINE
Python for Data Science
===========================================================================

Pipeline:

    Load
      ↓
    Parse
      ↓
    Clean / Preprocess
      ↓
    Label
      ↓
    Feature Engineering
      ↓
    Save

Input:
    Data/raw/cj.log

Outputs:
    Data/processed/pipeline_features.csv
    outputs/reports/practical_10_pipeline_report.txt

Important:
    The actual cj.log source does not contain HTTP method, URL/path,
    HTTP status or bytes fields. Therefore these fields are not invented.
"""

from pathlib import Path
import csv
import json
import math
import re
from collections import Counter, defaultdict

import pandas as pd


# =========================================================================
# CONFIGURATION
# =========================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "Data" / "raw" / "cj.log"

PROCESSED_DIR = BASE_DIR / "Data" / "processed"
REPORT_DIR = BASE_DIR / "outputs" / "reports"

INTERMEDIATE_FILE = (
    PROCESSED_DIR /
    "pipeline_cleaned_labeled.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR /
    "pipeline_features.csv"
)

REPORT_FILE = (
    REPORT_DIR /
    "practical_10_pipeline_report.txt"
)

CHUNK_SIZE = 50_000

# Keep these consistent with Practical 4/5.
SCANNER_PATTERNS = [
    "gobuster",
    "dirbuster",
    "nmap",
    "nikto",
    "zgrab",
    "nessus",
    "masscan",
    "wpscan"
]

BOT_PATTERNS = [
    "python-requests",
    "go-http-client",
    "bot",
    "spider",
    "curl",
    "crawler"
]


# =========================================================================
# DIRECTORY SETUP
# =========================================================================

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================================
# HELPER FUNCTIONS
# =========================================================================

def string_entropy(value):
    """
    Calculate Shannon entropy for a string.
    """

    if value is None:
        return 0.0

    value = str(value)

    if not value:
        return 0.0

    counts = Counter(value)
    length = len(value)

    entropy = 0.0

    for count in counts.values():

        probability = count / length

        entropy -= (
            probability *
            math.log2(probability)
        )

    return entropy


def detect_scanner(user_agent):
    """
    Detect known scanner/security-tool indicators.
    """

    text = str(user_agent).lower()

    for pattern in SCANNER_PATTERNS:

        if pattern in text:
            return pattern

    return "none"


def detect_bot(user_agent):
    """
    Detect common automated/bot clients.
    """

    text = str(user_agent).lower()

    for pattern in BOT_PATTERNS:

        if pattern in text:
            return pattern

    return "none"


def detect_browser(user_agent):
    """
    Detect common browser User-Agent strings.
    """

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


def classify_request(scanner_type, bot_type, rapid_1s):
    """
    Assign the same practical-style priority:

    scanner > bot > suspicious > benign
    """

    if scanner_type != "none":
        return "scanner"

    if bot_type != "none":
        return "bot"

    if rapid_1s:
        return "suspicious"

    return "benign"


def parse_raw_line(line):
    """
    Parse one JSON-array log record.

    Actual source structure:

    [
        null,
        null,
        timestamp,
        ip,
        port,
        user_agent,
        language,
        metadata
    ]
    """

    try:

        record = json.loads(line)

    except (json.JSONDecodeError, TypeError):

        return None

    if not isinstance(record, list):
        return None

    if len(record) != 8:
        return None

    return {
        "timestamp": record[2],
        "ip": record[3],
        "port": record[4],
        "user_agent": record[5],
        "language": record[6],
        "metadata": record[7]
    }


def clean_text(value):
    """
    Convert missing text to unknown and normalize strings.
    """

    if value is None:
        return "unknown"

    value = str(value).strip().lower()

    if not value:
        return "unknown"

    return value


# =========================================================================
# STEP 1 + 2
# LOAD AND PARSE
# =========================================================================

def load_and_parse():

    print("\n" + "=" * 75)
    print("STEP 1 + 2 - LOAD AND PARSE")
    print("=" * 75)

    if not RAW_FILE.exists():

        raise FileNotFoundError(
            f"Raw log file not found: {RAW_FILE}"
        )

    print(f"Input file : {RAW_FILE}")
    print("Input file status: FOUND")

    valid_records = 0
    invalid_json = 0
    invalid_structure = 0

    rows = []

    header = [
        "timestamp",
        "ip",
        "port",
        "user_agent",
        "language",
        "metadata"
    ]

    with open(
        RAW_FILE,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as source, open(
        INTERMEDIATE_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as destination:

        writer = csv.DictWriter(
            destination,
            fieldnames=header
        )

        writer.writeheader()

        for line_number, line in enumerate(
            source,
            start=1
        ):

            if not line.strip():
                continue

            try:

                record = json.loads(line)

            except json.JSONDecodeError:

                invalid_json += 1
                continue

            if not isinstance(record, list) or len(record) != 8:

                invalid_structure += 1
                continue

            row = {
                "timestamp": record[2],
                "ip": record[3],
                "port": record[4],
                "user_agent": record[5],
                "language": record[6],
                "metadata": record[7]
            }

            rows.append(row)

            if len(rows) >= CHUNK_SIZE:

                writer.writerows(rows)

                valid_records += len(rows)

                rows = []

                print(
                    f"Parsed records: "
                    f"{valid_records:,}",
                    end="\r"
                )

        if rows:

            writer.writerows(rows)
            valid_records += len(rows)

    print()

    print(
        f"Valid parsed records : "
        f"{valid_records:,}"
    )

    print(
        f"Invalid JSON records : "
        f"{invalid_json:,}"
    )

    print(
        f"Invalid structures   : "
        f"{invalid_structure:,}"
    )


# =========================================================================
# STEP 3 + 4
# CLEAN + LABEL
# =========================================================================

def clean_and_label():

    print("\n" + "=" * 75)
    print("STEP 3 + 4 - CLEAN / PREPROCESS + LABEL")
    print("=" * 75)

    total_rows = 0

    label_counts = Counter()

    # We'll overwrite the intermediate file with the cleaned/labelled data
    cleaned_file = (
        PROCESSED_DIR /
        "pipeline_cleaned.csv"
    )

    reader_chunks = pd.read_csv(
        INTERMEDIATE_FILE,
        chunksize=CHUNK_SIZE,
        dtype={
            "ip": "string",
            "user_agent": "string",
            "language": "string",
            "metadata": "string"
        }
    )

    first_chunk = True

    for chunk_number, df in enumerate(
        reader_chunks,
        start=1
    ):

        # ---------------------------------------------------------------
        # Clean strings
        # ---------------------------------------------------------------

        for column in [
            "ip",
            "user_agent",
            "language",
            "metadata"
        ]:

            df[column] = (
                df[column]
                .fillna("unknown")
                .astype(str)
                .str.strip()
                .str.lower()
            )

            df[column] = df[column].replace(
                "",
                "unknown"
            )

        # ---------------------------------------------------------------
        # Timestamp
        # ---------------------------------------------------------------

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

        # ---------------------------------------------------------------
        # Port
        # ---------------------------------------------------------------

        df["port"] = pd.to_numeric(
            df["port"],
            errors="coerce"
        )

        df["port"] = (
            df["port"]
            .fillna(-1)
            .astype("int64")
        )

        # ---------------------------------------------------------------
        # Drop invalid timestamps/IPs
        # ---------------------------------------------------------------

        df = df.dropna(
            subset=[
                "timestamp",
                "ip"
            ]
        ).copy()

        # ---------------------------------------------------------------
        # Scanner / Bot indicators
        # ---------------------------------------------------------------

        df["scanner_type"] = (
            df["user_agent"]
            .apply(detect_scanner)
        )

        df["bot_type"] = (
            df["user_agent"]
            .apply(detect_bot)
        )

        # ---------------------------------------------------------------
        # Sort chunk by IP/time
        # ---------------------------------------------------------------

        df = df.sort_values(
            [
                "ip",
                "timestamp"
            ]
        )

        # ---------------------------------------------------------------
        # Time between requests
        # ---------------------------------------------------------------

        df["time_between_requests"] = (
            df.groupby("ip")["timestamp"]
            .diff()
            .dt.total_seconds()
        )

        df["rapid_request_1s"] = (
            df["time_between_requests"]
            .fillna(999999)
            <= 1
        )

        # ---------------------------------------------------------------
        # Label
        # ---------------------------------------------------------------

        df["label"] = df.apply(
            lambda row: classify_request(
                row["scanner_type"],
                row["bot_type"],
                row["rapid_request_1s"]
            ),
            axis=1
        )

        counts = (
            df["label"]
            .value_counts()
            .to_dict()
        )

        label_counts.update(counts)

        # ---------------------------------------------------------------
        # Write chunk
        # ---------------------------------------------------------------

        df.to_csv(
            cleaned_file,
            mode="w" if first_chunk else "a",
            header=first_chunk,
            index=False
        )

        first_chunk = False

        total_rows += len(df)

        print(
            f"Processed chunks: {chunk_number} | "
            f"Rows: {total_rows:,}",
            end="\r"
        )

    print()

    print(
        f"Cleaned records: "
        f"{total_rows:,}"
    )

    print("\nLabel distribution:")

    for label, count in label_counts.most_common():

        print(
            f"{label:<15} {count:,}"
        )

    return cleaned_file


# =========================================================================
# STEP 5
# FEATURE ENGINEERING
# =========================================================================

def feature_engineering(cleaned_file):

    print("\n" + "=" * 75)
    print("STEP 5 - FEATURE ENGINEERING")
    print("=" * 75)

    print("Reading cleaned and labelled dataset...")

    df = pd.read_csv(
        cleaned_file,
        parse_dates=["timestamp"]
    )

    print(
        f"Rows loaded: "
        f"{len(df):,}"
    )

    # ---------------------------------------------------------------------
    # IP-level statistics
    # ---------------------------------------------------------------------

    print("Creating IP-level features...")

    ip_group = df.groupby("ip")

    request_counts = (
        ip_group.size()
        .rename("requests_per_ip")
    )

    unique_ports = (
        ip_group["port"]
        .nunique()
        .rename("unique_ports_per_ip")
    )

    first_seen = (
        ip_group["timestamp"]
        .min()
        .rename("ip_first_seen")
    )

    last_seen = (
        ip_group["timestamp"]
        .max()
        .rename("ip_last_seen")
    )

    ip_features = pd.concat(
        [
            request_counts,
            unique_ports,
            first_seen,
            last_seen
        ],
        axis=1
    )

    ip_features[
        "ip_active_duration_seconds"
    ] = (
        ip_features["ip_last_seen"]
        - ip_features["ip_first_seen"]
    ).dt.total_seconds()

    df = df.merge(
        ip_features,
        left_on="ip",
        right_index=True,
        how="left"
    )

    # ---------------------------------------------------------------------
    # Time features
    # ---------------------------------------------------------------------

    print("Creating time-based features...")

    df = df.sort_values(
        [
            "ip",
            "timestamp"
        ]
    )

    df["time_between_requests"] = (
        df.groupby("ip")["timestamp"]
        .diff()
        .dt.total_seconds()
    )

    df["rapid_request_1s"] = (
        df["time_between_requests"]
        .fillna(999999)
        <= 1
    )

    df["rapid_request_5s"] = (
        df["time_between_requests"]
        .fillna(999999)
        <= 5
    )

    # ---------------------------------------------------------------------
    # Request rate
    # ---------------------------------------------------------------------

    print("Creating request-rate features...")

    df["request_minute"] = (
        df["timestamp"]
        .dt.floor("1min")
    )

    df["request_hour"] = (
        df["timestamp"]
        .dt.floor("1h")
    )

    df["requests_per_ip_minute"] = (
        df.groupby(
            [
                "ip",
                "request_minute"
            ]
        )["ip"]
        .transform("size")
    )

    df["requests_per_ip_hour"] = (
        df.groupby(
            [
                "ip",
                "request_hour"
            ]
        )["ip"]
        .transform("size")
    )

    # ---------------------------------------------------------------------
    # User-Agent
    # ---------------------------------------------------------------------

    print("Creating User-Agent features...")

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
        .astype(str)
        .str.len()
    )

    df["user_agent_entropy"] = (
        df["user_agent"]
        .apply(string_entropy)
    )

    # ---------------------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------------------

    print("Creating metadata features...")

    df["metadata_present"] = (
        df["metadata"] != "unknown"
    )

    df["metadata_length"] = (
        df["metadata"]
        .astype(str)
        .str.len()
    )

    df["metadata_entropy"] = (
        df["metadata"]
        .apply(string_entropy)
    )

    # ---------------------------------------------------------------------
    # Language
    # ---------------------------------------------------------------------

    print("Creating language features...")

    df["language_present"] = (
        df["language"] != "unknown"
    )

    df["language_length"] = (
        df["language"]
        .astype(str)
        .str.len()
    )

    # ---------------------------------------------------------------------
    # Calendar
    # ---------------------------------------------------------------------

    print("Creating calendar features...")

    df["year"] = (
        df["timestamp"]
        .dt.year
    )

    df["month"] = (
        df["timestamp"]
        .dt.month
    )

    df["day"] = (
        df["timestamp"]
        .dt.day
    )

    df["hour"] = (
        df["timestamp"]
        .dt.hour
    )

    df["day_of_week"] = (
        df["timestamp"]
        .dt.dayofweek
    )

    df["is_weekend"] = (
        df["day_of_week"] >= 5
    )

    # ---------------------------------------------------------------------
    # Port
    # ---------------------------------------------------------------------

    print("Creating port features...")

    df["is_low_port"] = (
        (df["port"] >= 0) &
        (df["port"] < 1024)
    )

    df["is_ephemeral_port"] = (
        (df["port"] >= 49152) &
        (df["port"] <= 65535)
    )

    # ---------------------------------------------------------------------
    # Behavioral features
    # ---------------------------------------------------------------------

    print("Creating behavioral features...")

    df["high_volume_ip"] = (
        df["requests_per_ip"] >= 1000
    )

    df["very_high_volume_ip"] = (
        df["requests_per_ip"] >= 10000
    )

    df["scanner_and_high_volume"] = (
        df["is_scanner"] &
        df["high_volume_ip"]
    )

    df["rapid_and_high_volume"] = (
        df["rapid_request_1s"] &
        df["high_volume_ip"]
    )

    df["automated_activity"] = (
        df["is_scanner"] |
        df["is_bot"]
    )

    # ---------------------------------------------------------------------
    # Remove temporary columns
    # ---------------------------------------------------------------------

    df = df.drop(
        columns=[
            "request_minute",
            "request_hour"
        ],
        errors="ignore"
    )

    # ---------------------------------------------------------------------
    # Save final output
    # ---------------------------------------------------------------------

    print("\nSaving final pipeline dataset...")

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    return df


# =========================================================================
# MAIN
# =========================================================================

def main():

    print("=" * 75)
    print("PRACTICAL 10 - REUSABLE DATA SCIENCE PIPELINE")
    print("=" * 75)

    print("\nPipeline:")
    print("LOAD → PARSE → CLEAN → LABEL → FEATURE ENGINEERING → SAVE")

    # ---------------------------------------------------------------------
    # STEP 1 + 2
    # ---------------------------------------------------------------------

    load_and_parse()

    # ---------------------------------------------------------------------
    # STEP 3 + 4
    # ---------------------------------------------------------------------

    cleaned_file = clean_and_label()

    # ---------------------------------------------------------------------
    # STEP 5
    # ---------------------------------------------------------------------

    final_df = feature_engineering(
        cleaned_file
    )

    # ---------------------------------------------------------------------
    # VERIFICATION
    # ---------------------------------------------------------------------

    print("\n" + "=" * 75)
    print("PIPELINE OUTPUT VERIFICATION")
    print("=" * 75)

    print(
        f"Output file : "
        f"{OUTPUT_FILE}"
    )

    print(
        f"Rows        : "
        f"{len(final_df):,}"
    )

    print(
        f"Columns     : "
        f"{len(final_df.columns):,}"
    )

    if OUTPUT_FILE.exists():

        size_mb = (
            OUTPUT_FILE.stat().st_size
            / (1024 * 1024)
        )

        print(
            f"Output size : "
            f"{size_mb:.2f} MB"
        )

    print("\nFinal label distribution:")

    print(
        final_df["label"]
        .value_counts()
        .to_string()
    )

    print("\nFinal feature columns:")

    for number, column in enumerate(
        final_df.columns,
        start=1
    ):

        print(
            f"{number:2d}. {column}"
        )

    # ---------------------------------------------------------------------
    # SAMPLE
    # ---------------------------------------------------------------------

    print("\n" + "=" * 75)
    print("FINAL DATA SAMPLE")
    print("=" * 75)

    sample_columns = [
        "timestamp",
        "ip",
        "port",
        "label",
        "requests_per_ip",
        "unique_ports_per_ip",
        "time_between_requests",
        "requests_per_ip_minute",
        "requests_per_ip_hour",
        "is_scanner",
        "is_bot",
        "is_browser",
        "user_agent_entropy",
        "metadata_entropy",
        "high_volume_ip",
        "automated_activity"
    ]

    available_columns = [
        column
        for column in sample_columns
        if column in final_df.columns
    ]

    print(
        final_df[
            available_columns
        ]
        .head(10)
        .to_string(index=False)
    )

    # ---------------------------------------------------------------------
    # REPORT
    # ---------------------------------------------------------------------

    report = []

    report.append("=" * 75)
    report.append("PRACTICAL 10 - REUSABLE PIPELINE REPORT")
    report.append("=" * 75)
    report.append("")

    report.append("PIPELINE STAGES")
    report.append("-" * 75)
    report.append("1. Load raw cj.log")
    report.append("2. Parse JSON records")
    report.append("3. Clean and preprocess")
    report.append("4. Label requests")
    report.append("5. Engineer features")
    report.append("6. Save final dataset")
    report.append("")

    report.append("INPUT")
    report.append("-" * 75)
    report.append(f"Input file: {RAW_FILE}")
    report.append("")

    report.append("OUTPUT")
    report.append("-" * 75)
    report.append(f"Output file: {OUTPUT_FILE}")
    report.append(
        f"Rows: {len(final_df):,}"
    )
    report.append(
        f"Columns: {len(final_df.columns):,}"
    )

    if OUTPUT_FILE.exists():

        report.append(
            f"Size: "
            f"{OUTPUT_FILE.stat().st_size / (1024 * 1024):.2f} MB"
        )

    report.append("")

    report.append("LABEL DISTRIBUTION")
    report.append("-" * 75)

    label_counts = (
        final_df["label"]
        .value_counts()
    )

    for label, count in label_counts.items():

        percentage = (
            count /
            len(final_df) *
            100
        )

        report.append(
            f"{label:<15} "
            f"{count:>10,} "
            f"({percentage:.2f}%)"
        )

    report.append("")

    report.append("SOURCE DATA LIMITATION")
    report.append("-" * 75)
    report.append(
        "The actual cj.log source does not contain HTTP method, "
        "URL/request path, HTTP status code, or response-byte fields."
    )
    report.append(
        "Therefore these unavailable fields are not fabricated "
        "by the pipeline."
    )

    report.append("")

    report.append("REUSABILITY")
    report.append("-" * 75)
    report.append(
        "The pipeline can be rerun against the raw cj.log file "
        "to reproduce parsing, preprocessing, labeling, feature "
        "engineering, and final dataset generation."
    )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "\n".join(report)
        )

    print("\nReport saved to:")
    print(REPORT_FILE)

    print("\n" + "=" * 75)
    print("PRACTICAL 10 COMPLETED SUCCESSFULLY")
    print("=" * 75)


# =========================================================================
# ENTRY POINT
# =========================================================================

if __name__ == "__main__":
    main()