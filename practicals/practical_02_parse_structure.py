"""
Practical 2: Convert Unstructured Log Data into a Structured Dataset

Dataset:
    Data/raw/cj.log

Output:
    Data/processed/structured_logs.csv

Objective:
    Parse the semi-structured log records and convert them
    into a structured Pandas dataset.
"""

import json
from pathlib import Path
from collections import Counter

import pandas as pd


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

LOG_FILE = BASE_DIR / "Data" / "raw" / "cj.log"
PROCESSED_DIR = BASE_DIR / "Data" / "processed"
OUTPUT_FILE = PROCESSED_DIR / "structured_logs.csv"

REPORT_DIR = BASE_DIR / "outputs" / "reports"
REPORT_FILE = REPORT_DIR / "practical_02_schema_report.txt"


# ============================================================
# 2. SETTINGS
# ============================================================

# Number of records converted into one Pandas DataFrame
# before writing to CSV.
CHUNK_SIZE = 50_000


# ============================================================
# 3. CREATE OUTPUT DIRECTORIES
# ============================================================

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 4. CHECK INPUT FILE
# ============================================================

print("=" * 75)
print("PRACTICAL 2 - PARSE AND STRUCTURE LOG DATA")
print("=" * 75)

print(f"\nInput file: {LOG_FILE}")

if not LOG_FILE.exists():
    raise FileNotFoundError(
        f"Log file not found:\n{LOG_FILE}"
    )

print("File status: FOUND")


# ============================================================
# 5. OUTPUT COLUMNS
# ============================================================

# These columns are based on the actual schema discovered
# during Practical 1.

COLUMN_NAMES = [
    "timestamp",
    "ip",
    "port",
    "user_agent",
    "language",
    "metadata"
]


# ============================================================
# 6. PROCESS THE LOG FILE
# ============================================================

print("\nStarting parsing and structuring...")
print(f"Chunk size: {CHUNK_SIZE:,} records")

total_lines = 0
valid_records = 0
invalid_json = 0
invalid_structure = 0
wrong_field_count = 0

field_count_distribution = Counter()

missing_counts = Counter()

chunk = []
chunk_number = 0

# Remove old output file if it exists.
if OUTPUT_FILE.exists():
    OUTPUT_FILE.unlink()


with LOG_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace"
) as file:

    for line_number, line in enumerate(file, start=1):

        total_lines += 1

        line = line.strip()

        # ----------------------------------------------------
        # Skip empty lines
        # ----------------------------------------------------

        if not line:
            continue

        # ----------------------------------------------------
        # Parse JSON
        # ----------------------------------------------------

        try:
            record = json.loads(line)

        except json.JSONDecodeError:

            invalid_json += 1
            continue

        # ----------------------------------------------------
        # Check record type
        # ----------------------------------------------------

        if not isinstance(record, list):

            invalid_structure += 1
            continue

        # ----------------------------------------------------
        # Record field count
        # ----------------------------------------------------

        field_count = len(record)

        field_count_distribution[field_count] += 1

        if field_count != 8:

            wrong_field_count += 1
            continue

        # ----------------------------------------------------
        # Extract useful fields
        # ----------------------------------------------------

        structured_record = {
            "timestamp": record[2],
            "ip": record[3],
            "port": record[4],
            "user_agent": record[5],
            "language": record[6],
            "metadata": record[7]
        }

        # ----------------------------------------------------
        # Count missing values
        # ----------------------------------------------------

        for column, value in structured_record.items():

            if value is None or value == "":

                missing_counts[column] += 1

        # ----------------------------------------------------
        # Add record to current chunk
        # ----------------------------------------------------

        chunk.append(structured_record)

        valid_records += 1

        # ----------------------------------------------------
        # Convert chunk to Pandas DataFrame
        # ----------------------------------------------------

        if len(chunk) >= CHUNK_SIZE:

            chunk_number += 1

            df_chunk = pd.DataFrame(
                chunk,
                columns=COLUMN_NAMES
            )

            # Write header only for first chunk.
            df_chunk.to_csv(
                OUTPUT_FILE,
                mode="w" if chunk_number == 1 else "a",
                header=(chunk_number == 1),
                index=False
            )

            print(
                f"Chunk {chunk_number:>3}: "
                f"{valid_records:,} records processed"
            )

            chunk.clear()


# ============================================================
# 7. WRITE REMAINING RECORDS
# ============================================================

if chunk:

    chunk_number += 1

    df_chunk = pd.DataFrame(
        chunk,
        columns=COLUMN_NAMES
    )

    df_chunk.to_csv(
        OUTPUT_FILE,
        mode="w" if chunk_number == 1 else "a",
        header=(chunk_number == 1),
        index=False
    )

    print(
        f"Chunk {chunk_number:>3}: "
        f"{valid_records:,} records processed"
    )

    chunk.clear()


# ============================================================
# 8. VERIFY OUTPUT FILE
# ============================================================

print("\n" + "-" * 75)
print("OUTPUT VERIFICATION")
print("-" * 75)

if OUTPUT_FILE.exists():

    output_size_mb = (
        OUTPUT_FILE.stat().st_size
        / (1024 * 1024)
    )

    print(f"Output file : {OUTPUT_FILE}")
    print(f"Output size : {output_size_mb:.2f} MB")

else:

    print("ERROR: Output CSV was not created.")


# ============================================================
# 9. READ SMALL SAMPLE USING PANDAS
# ============================================================

print("\n" + "-" * 75)
print("STRUCTURED DATA SAMPLE")
print("-" * 75)

if OUTPUT_FILE.exists():

    sample_df = pd.read_csv(
        OUTPUT_FILE,
        nrows=10
    )

    print("\nDataFrame:")
    print(sample_df.to_string(index=False))

    print("\nDataFrame columns:")
    print(list(sample_df.columns))

    print("\nData types:")
    print(sample_df.dtypes)


# ============================================================
# 10. FIELD COUNT DISTRIBUTION
# ============================================================

print("\n" + "-" * 75)
print("RAW FIELD COUNT DISTRIBUTION")
print("-" * 75)

for count, frequency in sorted(
    field_count_distribution.items()
):

    print(
        f"{count} fields : "
        f"{frequency:,} records"
    )


# ============================================================
# 11. MISSING VALUE SUMMARY
# ============================================================

print("\n" + "-" * 75)
print("MISSING VALUE SUMMARY")
print("-" * 75)

for column in COLUMN_NAMES:

    print(
        f"{column:15s}: "
        f"{missing_counts[column]:,}"
    )


# ============================================================
# 12. PROCESSING SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("PRACTICAL 2 PROCESSING SUMMARY")
print("=" * 75)

print(f"Total lines read       : {total_lines:,}")
print(f"Valid structured rows  : {valid_records:,}")
print(f"Invalid JSON records   : {invalid_json:,}")
print(f"Invalid structures     : {invalid_structure:,}")
print(f"Wrong field count      : {wrong_field_count:,}")
print(f"Chunks created         : {chunk_number}")
print(f"Output CSV             : {OUTPUT_FILE}")

print("\nStructured columns:")

for column in COLUMN_NAMES:

    print(f"  - {column}")


# ============================================================
# 13. SAVE REPORT
# ============================================================

with REPORT_FILE.open(
    "w",
    encoding="utf-8"
) as report:

    report.write(
        "PRACTICAL 2 - LOG STRUCTURING REPORT\n"
    )

    report.write("=" * 60 + "\n\n")

    report.write(
        f"Input file: {LOG_FILE}\n"
    )

    report.write(
        f"Total lines read: {total_lines:,}\n"
    )

    report.write(
        f"Valid structured rows: {valid_records:,}\n"
    )

    report.write(
        f"Invalid JSON records: {invalid_json:,}\n"
    )

    report.write(
        f"Invalid structures: {invalid_structure:,}\n"
    )

    report.write(
        f"Wrong field count: {wrong_field_count:,}\n"
    )

    report.write(
        f"Chunks created: {chunk_number}\n\n"
    )

    report.write("Structured columns:\n")

    for column in COLUMN_NAMES:

        report.write(
            f"- {column}\n"
        )

    report.write("\nRaw field count distribution:\n")

    for count, frequency in sorted(
        field_count_distribution.items()
    ):

        report.write(
            f"{count} fields: "
            f"{frequency:,} records\n"
        )

    report.write("\nMissing values:\n")

    for column in COLUMN_NAMES:

        report.write(
            f"{column}: "
            f"{missing_counts[column]:,}\n"
        )


# ============================================================
# 14. FINAL MESSAGE
# ============================================================

print("\nReport saved to:")
print(REPORT_FILE)

print("\n" + "=" * 75)
print("PRACTICAL 2 COMPLETED SUCCESSFULLY")
print("=" * 75)