"""
Practical 3: Data Cleaning and Preprocessing

Input:
    Data/processed/structured_logs.csv

Output:
    Data/processed/cleaned_logs.csv

Objective:
    Clean and preprocess the structured access-log dataset.
"""

from pathlib import Path
import ipaddress

import pandas as pd


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "Data"
    / "processed"
    / "structured_logs.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "Data"
    / "processed"
    / "cleaned_logs.csv"
)

REPORT_DIR = (
    BASE_DIR
    / "outputs"
    / "reports"
)

REPORT_FILE = (
    REPORT_DIR
    / "practical_03_cleaning_report.txt"
)


# ============================================================
# 2. SETTINGS
# ============================================================

CHUNK_SIZE = 50_000


# ============================================================
# 3. CREATE REPORT DIRECTORY
# ============================================================

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 4. CHECK INPUT FILE
# ============================================================

print("=" * 75)
print("PRACTICAL 3 - DATA CLEANING AND PREPROCESSING")
print("=" * 75)

print(f"\nInput file: {INPUT_FILE}")

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input file not found:\n{INPUT_FILE}"
    )

print("Input file status: FOUND")


# ============================================================
# 5. CLEANING FUNCTIONS
# ============================================================

def clean_text(value):
    """
    Remove leading/trailing spaces and convert text to lowercase.
    Missing values are replaced with 'unknown'.
    """

    if pd.isna(value):
        return "unknown"

    value = str(value).strip().lower()

    if value == "":
        return "unknown"

    return value


def validate_ip(value):
    """
    Validate IPv4 or IPv6 address.
    """

    if pd.isna(value):
        return False

    try:
        ipaddress.ip_address(str(value).strip())
        return True

    except ValueError:
        return False


# ============================================================
# 6. REMOVE OLD OUTPUT
# ============================================================

if OUTPUT_FILE.exists():
    OUTPUT_FILE.unlink()


# ============================================================
# 7. INITIALIZE STATISTICS
# ============================================================

total_rows = 0
invalid_timestamps = 0
invalid_ips = 0
invalid_ports = 0

missing_before = {
    "timestamp": 0,
    "ip": 0,
    "port": 0,
    "user_agent": 0,
    "language": 0,
    "metadata": 0
}

chunk_number = 0


# ============================================================
# 8. PROCESS DATA IN CHUNKS
# ============================================================

print("\nStarting cleaning process...")
print(f"Chunk size: {CHUNK_SIZE:,} records")


for df in pd.read_csv(
    INPUT_FILE,
    chunksize=CHUNK_SIZE,
    dtype={
        "timestamp": "string",
        "ip": "string",
        "port": "string",
        "user_agent": "string",
        "language": "string",
        "metadata": "string"
    },
    keep_default_na=True
):

    chunk_number += 1
    total_rows += len(df)

    # ========================================================
    # A. MISSING VALUES BEFORE CLEANING
    # ========================================================

    for column in missing_before:

        missing_before[column] += (
            df[column].isna().sum()
        )

    # ========================================================
    # B. TIMESTAMP CLEANING
    # ========================================================

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    invalid_timestamps += (
        df["timestamp"].isna().sum()
    )

    # ========================================================
    # C. IP ADDRESS CLEANING
    # ========================================================

    df["ip"] = (
        df["ip"]
        .astype("string")
        .str.strip()
    )

    df["ip_valid"] = df["ip"].apply(
        validate_ip
    )

    invalid_ips += (
        (~df["ip_valid"]).sum()
    )

    # ========================================================
    # D. PORT CLEANING
    # ========================================================

    df["port"] = pd.to_numeric(
        df["port"],
        errors="coerce"
    )

    df["port_valid"] = df["port"].between(
        0,
        65535
    )

    invalid_ports += (
        (~df["port_valid"]).sum()
    )

    # ========================================================
    # E. USER-AGENT CLEANING
    # ========================================================

    df["user_agent"] = (
        df["user_agent"]
        .apply(clean_text)
    )

    # ========================================================
    # F. LANGUAGE CLEANING
    # ========================================================

    df["language"] = (
        df["language"]
        .apply(clean_text)
    )

    # ========================================================
    # G. METADATA CLEANING
    # ========================================================

    df["metadata"] = (
        df["metadata"]
        .apply(clean_text)
    )

    # ========================================================
    # H. MISSING VALUE INDICATORS
    # ========================================================

    df["user_agent_missing"] = (
        df["user_agent"] == "unknown"
    )

    df["language_missing"] = (
        df["language"] == "unknown"
    )

    df["metadata_missing"] = (
        df["metadata"] == "unknown"
    )

    # ========================================================
    # I. WRITE CLEANED DATA
    # ========================================================

    df.to_csv(
        OUTPUT_FILE,
        mode="w" if chunk_number == 1 else "a",
        header=(chunk_number == 1),
        index=False
    )

    # ========================================================
    # J. PROGRESS
    # ========================================================

    if (
        chunk_number == 1
        or chunk_number % 5 == 0
    ):

        print(
            f"Chunk {chunk_number:>3}: "
            f"{total_rows:,} rows cleaned"
        )


# ============================================================
# 9. VERIFY OUTPUT
# ============================================================

print("\n" + "-" * 75)
print("CLEANED DATASET VERIFICATION")
print("-" * 75)

if OUTPUT_FILE.exists():

    output_size_mb = (
        OUTPUT_FILE.stat().st_size
        / (1024 * 1024)
    )

    print(f"Output file : {OUTPUT_FILE}")
    print(f"Output size : {output_size_mb:.2f} MB")

else:

    raise FileNotFoundError(
        "Cleaned dataset was not created."
    )


# ============================================================
# 10. READ SMALL SAMPLE
# ============================================================

cleaned_sample = pd.read_csv(
    OUTPUT_FILE,
    nrows=10
)

print("\nCleaned DataFrame sample:")
print(
    cleaned_sample.to_string(
        index=False
    )
)


# ============================================================
# 11. DATA TYPES
# ============================================================

print("\n" + "-" * 75)
print("CLEANED DATA TYPES")
print("-" * 75)

print(cleaned_sample.dtypes)


# ============================================================
# 12. FINAL MISSING VALUE CHECK
# ============================================================

print("\n" + "-" * 75)
print("FINAL MISSING VALUE CHECK - SAMPLE")
print("-" * 75)

print(cleaned_sample.isna().sum())


# ============================================================
# 13. SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("PRACTICAL 3 CLEANING SUMMARY")
print("=" * 75)

print(f"Rows processed       : {total_rows:,}")
print(f"Invalid timestamps   : {invalid_timestamps:,}")
print(f"Invalid IP addresses: {invalid_ips:,}")
print(f"Invalid ports       : {invalid_ports:,}")
print(f"Chunks processed    : {chunk_number}")

print("\nMissing values before cleaning:")

for column, count in missing_before.items():

    print(
        f"  {column:15s}: {count:,}"
    )

print("\nCleaning operations performed:")

print("  - Timestamp converted to datetime")
print("  - IP addresses validated")
print("  - Port values converted to numeric")
print("  - User-agent strings cleaned")
print("  - Language strings cleaned")
print("  - Metadata strings cleaned")
print("  - Missing text values replaced with 'unknown'")
print("  - Missing-value indicator columns created")

print("\nURL/path normalization:")

print(
    "  Not performed because the source dataset "
    "does not contain a URL/request-path field."
)


# ============================================================
# 14. SAVE REPORT
# ============================================================

with REPORT_FILE.open(
    "w",
    encoding="utf-8"
) as report:

    report.write(
        "PRACTICAL 3 - DATA CLEANING REPORT\n"
    )

    report.write("=" * 60 + "\n\n")

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
        f"Invalid timestamps: "
        f"{invalid_timestamps:,}\n"
    )

    report.write(
        f"Invalid IP addresses: "
        f"{invalid_ips:,}\n"
    )

    report.write(
        f"Invalid ports: "
        f"{invalid_ports:,}\n\n"
    )

    report.write(
        "Missing values before cleaning:\n"
    )

    for column, count in missing_before.items():

        report.write(
            f"{column}: {count:,}\n"
        )

    report.write(
        "\nCleaning operations:\n"
    )

    report.write(
        "- Timestamp converted to datetime\n"
    )

    report.write(
        "- IP addresses validated\n"
    )

    report.write(
        "- Port values converted to numeric\n"
    )

    report.write(
        "- Text values stripped and lowercased\n"
    )

    report.write(
        "- Missing text values replaced with 'unknown'\n"
    )

    report.write(
        "- Missing-value indicator columns created\n"
    )

    report.write(
        "\nURL/path normalization was not performed "
        "because no URL/request-path field exists "
        "in the source dataset.\n"
    )


# ============================================================
# 15. COMPLETION
# ============================================================

print("\nReport saved to:")
print(REPORT_FILE)

print("\n" + "=" * 75)
print("PRACTICAL 3 COMPLETED SUCCESSFULLY")
print("=" * 75)