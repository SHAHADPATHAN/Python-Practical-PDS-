"""
Practical 4: Label Requests as Benign or Suspicious Activity

Input:
    Data/processed/cleaned_logs.csv

Output:
    Data/processed/labeled_logs.csv

Objective:
    Detect observable suspicious/automated activity from
    the available log fields and create a classification label.

Labels:
    benign
    bot
    scanner
    suspicious
"""

from pathlib import Path

import pandas as pd


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "Data"
    / "processed"
    / "cleaned_logs.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "Data"
    / "processed"
    / "labeled_logs.csv"
)

REPORT_DIR = (
    BASE_DIR
    / "outputs"
    / "reports"
)

REPORT_FILE = (
    REPORT_DIR
    / "practical_04_labeling_report.txt"
)


# ============================================================
# 2. SETTINGS
# ============================================================

CHUNK_SIZE = 50_000


# ============================================================
# 3. CHECK INPUT
# ============================================================

print("=" * 75)
print("PRACTICAL 4 - ATTACK / SUSPICIOUS ACTIVITY LABELING")
print("=" * 75)

print(f"\nInput file: {INPUT_FILE}")

if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"Input file not found:\n{INPUT_FILE}"
    )

print("Input file status: FOUND")


# ============================================================
# 4. SUSPICIOUS USER-AGENT PATTERNS
# ============================================================

# These patterns indicate automated/security/scanning tools.
# They are evidence-based indicators, not proof of maliciousness.

SCANNER_PATTERNS = [
    "gobuster",
    "dirbuster",
    "nikto",
    "wpscan",
    "masscan",
    "nmap",
    "sqlmap",
    "acunetix",
    "nessus",
    "openvas",
    "burp",
    "zgrab",
    "nuclei",
]

BOT_PATTERNS = [
    "bot",
    "crawler",
    "spider",
    "scrapy",
    "python-requests",
    "python-urllib",
    "go-http-client",
    "curl/",
    "wget/",
]


# ============================================================
# 5. HELPER FUNCTION
# ============================================================

def find_pattern(text, patterns):
    """
    Return the first matching pattern.
    Return 'none' when no pattern is found.
    """

    if pd.isna(text):

        return "none"

    text = str(text).lower()

    for pattern in patterns:

        if pattern in text:

            return pattern

    return "none"


# ============================================================
# 6. REMOVE OLD OUTPUT
# ============================================================

if OUTPUT_FILE.exists():

    OUTPUT_FILE.unlink()


# ============================================================
# 7. INITIALIZE STATISTICS
# ============================================================

total_rows = 0
chunk_number = 0

label_counts = {
    "benign": 0,
    "bot": 0,
    "scanner": 0,
    "suspicious": 0
}

scanner_pattern_counts = {}
bot_pattern_counts = {}

rapid_request_count = 0


# ============================================================
# 8. PROCESS DATA
# ============================================================

print("\nStarting labeling process...")
print(f"Chunk size: {CHUNK_SIZE:,} records")


for df in pd.read_csv(
    INPUT_FILE,
    chunksize=CHUNK_SIZE,
    dtype={
        "ip": "string",
        "user_agent": "string",
        "language": "string",
        "metadata": "string"
    },
    parse_dates=["timestamp"]
):

    chunk_number += 1

    total_rows += len(df)


    # ========================================================
    # A. USER-AGENT PATTERN DETECTION
    # ========================================================

    df["scanner_indicator"] = (
        df["user_agent"]
        .apply(
            lambda x:
            find_pattern(
                x,
                SCANNER_PATTERNS
            )
        )
    )

    df["bot_indicator"] = (
        df["user_agent"]
        .apply(
            lambda x:
            find_pattern(
                x,
                BOT_PATTERNS
            )
        )
    )


    # ========================================================
    # B. REQUEST COUNT PER IP
    # ========================================================

    # NOTE:
    # This chunk-level count is only an intermediate signal.
    # A full global IP frequency feature will be created
    # in Practical 5.

    ip_frequency = (
        df["ip"]
        .value_counts()
    )

    df["requests_in_chunk"] = (
        df["ip"]
        .map(ip_frequency)
    )


    # ========================================================
    # C. TIME BETWEEN REQUESTS
    # ========================================================

    # Sort this chunk by IP and timestamp so that consecutive
    # requests from the same IP can be compared.

    df = df.sort_values(
        ["ip", "timestamp"]
    )

    df["time_between_requests"] = (
        df.groupby("ip")["timestamp"]
        .diff()
        .dt.total_seconds()
    )


    # ========================================================
    # D. RAPID REQUEST INDICATOR
    # ========================================================

    df["rapid_request"] = (
        df["time_between_requests"]
        .notna()
        &
        (
            df["time_between_requests"] <= 1
        )
    )


    rapid_request_count += (
        df["rapid_request"].sum()
    )


    # ========================================================
    # E. CREATE LABEL
    # ========================================================

    def assign_label(row):

        # Strongest observable indicator:
        # known scanner/security tool.

        if row["scanner_indicator"] != "none":

            return "scanner"


        # Clearly automated client.

        if row["bot_indicator"] != "none":

            return "bot"


        # Rapid repeated activity is suspicious,
        # but not automatically an attack.

        if row["rapid_request"]:

            return "suspicious"


        return "benign"


    df["label"] = df.apply(
        assign_label,
        axis=1
    )


    # ========================================================
    # F. UPDATE COUNTS
    # ========================================================

    current_labels = (
        df["label"]
        .value_counts()
        .to_dict()
    )

    for label, count in current_labels.items():

        label_counts[label] = (
            label_counts.get(label, 0)
            + count
        )


    # Scanner indicators

    current_scanners = (
        df.loc[
            df["scanner_indicator"] != "none",
            "scanner_indicator"
        ]
        .value_counts()
        .to_dict()
    )

    for pattern, count in current_scanners.items():

        scanner_pattern_counts[pattern] = (
            scanner_pattern_counts.get(pattern, 0)
            + count
        )


    # Bot indicators

    current_bots = (
        df.loc[
            df["bot_indicator"] != "none",
            "bot_indicator"
        ]
        .value_counts()
        .to_dict()
    )

    for pattern, count in current_bots.items():

        bot_pattern_counts[pattern] = (
            bot_pattern_counts.get(pattern, 0)
            + count
        )


    # ========================================================
    # G. WRITE OUTPUT
    # ========================================================

    df.to_csv(
        OUTPUT_FILE,
        mode="w" if chunk_number == 1 else "a",
        header=(chunk_number == 1),
        index=False
    )


    # ========================================================
    # H. PROGRESS
    # ========================================================

    if (
        chunk_number == 1
        or chunk_number % 5 == 0
    ):

        print(
            f"Chunk {chunk_number:>3}: "
            f"{total_rows:,} rows labeled"
        )


# ============================================================
# 9. VERIFY OUTPUT
# ============================================================

print("\n" + "-" * 75)
print("LABELED DATASET VERIFICATION")
print("-" * 75)

if not OUTPUT_FILE.exists():

    raise FileNotFoundError(
        "Labeled dataset was not created."
    )

output_size_mb = (
    OUTPUT_FILE.stat().st_size
    / (1024 * 1024)
)

print(f"Output file : {OUTPUT_FILE}")
print(f"Output size : {output_size_mb:.2f} MB")


# ============================================================
# 10. LABEL DISTRIBUTION
# ============================================================

print("\n" + "-" * 75)
print("LABEL DISTRIBUTION")
print("-" * 75)

for label, count in sorted(
    label_counts.items(),
    key=lambda x: x[1],
    reverse=True
):

    percentage = (
        count / total_rows * 100
    )

    print(
        f"{label:12s}: "
        f"{count:>12,} "
        f"({percentage:6.2f}%)"
    )


# ============================================================
# 11. SCANNER INDICATORS
# ============================================================

print("\n" + "-" * 75)
print("SCANNER INDICATORS")
print("-" * 75)

if scanner_pattern_counts:

    for pattern, count in sorted(
        scanner_pattern_counts.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        print(
            f"{pattern:20s}: "
            f"{count:,}"
        )

else:

    print("No scanner indicators detected.")


# ============================================================
# 12. BOT INDICATORS
# ============================================================

print("\n" + "-" * 75)
print("BOT INDICATORS")
print("-" * 75)

if bot_pattern_counts:

    for pattern, count in sorted(
        bot_pattern_counts.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        print(
            f"{pattern:20s}: "
            f"{count:,}"
        )

else:

    print("No bot indicators detected.")


# ============================================================
# 13. RAPID REQUEST STATISTICS
# ============================================================

print("\n" + "-" * 75)
print("RAPID REQUEST ANALYSIS")
print("-" * 75)

print(
    f"Requests with <= 1 second gap: "
    f"{rapid_request_count:,}"
)


# ============================================================
# 14. SAMPLE OF LABELED DATA
# ============================================================

print("\n" + "-" * 75)
print("LABELED DATA SAMPLE")
print("-" * 75)

sample_df = pd.read_csv(
    OUTPUT_FILE,
    nrows=15,
    parse_dates=["timestamp"]
)

display_columns = [
    "timestamp",
    "ip",
    "user_agent",
    "scanner_indicator",
    "bot_indicator",
    "time_between_requests",
    "rapid_request",
    "label"
]

print(
    sample_df[
        display_columns
    ].to_string(index=False)
)


# ============================================================
# 15. SAVE REPORT
# ============================================================

with REPORT_FILE.open(
    "w",
    encoding="utf-8"
) as report:

    report.write(
        "PRACTICAL 4 - LABELING REPORT\n"
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
        f"Rows processed: {total_rows:,}\n"
    )

    report.write(
        f"Chunks processed: {chunk_number}\n\n"
    )

    report.write(
        "LABEL DISTRIBUTION\n"
    )

    for label, count in sorted(
        label_counts.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        percentage = (
            count / total_rows * 100
        )

        report.write(
            f"{label}: "
            f"{count:,} "
            f"({percentage:.2f}%)\n"
        )


    report.write(
        "\nSCANNER INDICATORS\n"
    )

    for pattern, count in sorted(
        scanner_pattern_counts.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        report.write(
            f"{pattern}: {count:,}\n"
        )


    report.write(
        "\nBOT INDICATORS\n"
    )

    for pattern, count in sorted(
        bot_pattern_counts.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        report.write(
            f"{pattern}: {count:,}\n"
        )


    report.write(
        "\nRAPID REQUEST ANALYSIS\n"
    )

    report.write(
        f"Requests with <= 1 second gap: "
        f"{rapid_request_count:,}\n"
    )


    report.write(
        "\nLABELING METHODOLOGY\n"
    )

    report.write(
        "scanner = known security/scanning "
        "tool indicator in User-Agent\n"
    )

    report.write(
        "bot = known automated client indicator "
        "in User-Agent\n"
    )

    report.write(
        "suspicious = rapid repeated request "
        "with <= 1 second gap\n"
    )

    report.write(
        "benign = no observable suspicious "
        "indicator detected\n"
    )

    report.write(
        "\nImportant limitation: the source dataset "
        "does not contain an explicit HTTP request "
        "path, method, or status code. Therefore, "
        "SQL injection and path traversal labels "
        "were not assigned without direct evidence.\n"
    )


# ============================================================
# 16. COMPLETION
# ============================================================

print("\nReport saved to:")
print(REPORT_FILE)

print("\n" + "=" * 75)
print("PRACTICAL 4 COMPLETED SUCCESSFULLY")
print("=" * 75)