"""
===========================================================================
PRACTICAL 6 - DATASET BALANCING
Python for Data Science
===========================================================================

Purpose:
    Analyze class imbalance and create a balanced dataset using
    controlled random undersampling.

Input:
    Data/processed/features.csv

Output:
    Data/processed/balanced_logs.csv
    outputs/reports/practical_06_balancing_report.txt
"""

from pathlib import Path
import pandas as pd


# =========================================================================
# CONFIGURATION
# =========================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "Data" / "processed" / "features.csv"
OUTPUT_DIR = BASE_DIR / "Data" / "processed"
REPORT_DIR = BASE_DIR / "outputs" / "reports"

OUTPUT_FILE = OUTPUT_DIR / "balanced_logs.csv"
REPORT_FILE = REPORT_DIR / "practical_06_balancing_report.txt"

RANDOM_STATE = 42


# =========================================================================
# HELPER FUNCTIONS
# =========================================================================

def print_separator():
    print("-" * 75)


def save_report(report_lines):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))


# =========================================================================
# MAIN
# =========================================================================

def main():

    print("=" * 75)
    print("PRACTICAL 6 - DATASET BALANCING")
    print("=" * 75)

    print(f"\nInput file: {INPUT_FILE}")

    if not INPUT_FILE.exists():
        print("ERROR: Input file not found.")
        print("Expected Practical 5 output:")
        print(INPUT_FILE)
        return

    print("Input file status: FOUND")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------------
    # LOAD DATA
    # ---------------------------------------------------------------------

    print("\nLoading feature dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows loaded    : {len(df):,}")
    print(f"Columns loaded : {len(df.columns)}")

    if "label" not in df.columns:
        print("\nERROR: 'label' column not found.")
        return

    # ---------------------------------------------------------------------
    # REMOVE INVALID LABELS
    # ---------------------------------------------------------------------

    print("\nChecking labels...")

    missing_labels = df["label"].isna().sum()

    print(f"Missing labels : {missing_labels:,}")

    if missing_labels > 0:
        df = df.dropna(subset=["label"]).copy()

    # ---------------------------------------------------------------------
    # ORIGINAL DISTRIBUTION
    # ---------------------------------------------------------------------

    print("\n" + "=" * 75)
    print("ORIGINAL CLASS DISTRIBUTION")
    print("=" * 75)

    original_counts = df["label"].value_counts()

    print(original_counts.to_string())

    original_percent = (
        df["label"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
    )

    print("\nOriginal class percentages:")
    for label, percentage in original_percent.items():
        print(f"{label:<15} {percentage:>8.2f}%")

    # ---------------------------------------------------------------------
    # IDENTIFY MINORITY CLASS
    # ---------------------------------------------------------------------

    min_class_count = original_counts.min()

    print("\n" + "=" * 75)
    print("BALANCING TARGET")
    print("=" * 75)

    print(f"Smallest class size : {min_class_count:,}")
    print("Balancing method    : Controlled Random Undersampling")
    print("Random state        :", RANDOM_STATE)

    print(
        "\nEach class will be randomly reduced to the size "
        "of the smallest class."
    )

    # ---------------------------------------------------------------------
    # BALANCE DATASET
    # ---------------------------------------------------------------------

    print("\nCreating balanced dataset...")

    balanced_parts = []

    for label in original_counts.index:

        class_df = df[df["label"] == label]

        sampled_class = class_df.sample(
            n=min_class_count,
            random_state=RANDOM_STATE
        )

        balanced_parts.append(sampled_class)

        print(
            f"{str(label):<15} "
            f"Original: {len(class_df):>10,}  "
            f"Selected: {len(sampled_class):>10,}"
        )

    balanced_df = pd.concat(
        balanced_parts,
        ignore_index=True
    )

    # Shuffle final dataset
    balanced_df = balanced_df.sample(
        frac=1,
        random_state=RANDOM_STATE
    ).reset_index(drop=True)

    # ---------------------------------------------------------------------
    # BALANCED DISTRIBUTION
    # ---------------------------------------------------------------------

    print("\n" + "=" * 75)
    print("BALANCED CLASS DISTRIBUTION")
    print("=" * 75)

    balanced_counts = balanced_df["label"].value_counts()

    print(balanced_counts.to_string())

    balanced_percent = (
        balanced_df["label"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
    )

    print("\nBalanced class percentages:")

    for label, percentage in balanced_percent.items():
        print(f"{label:<15} {percentage:>8.2f}%")

    # ---------------------------------------------------------------------
    # SAVE DATASET
    # ---------------------------------------------------------------------

    print("\nSaving balanced dataset...")

    balanced_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ---------------------------------------------------------------------
    # VERIFICATION
    # ---------------------------------------------------------------------

    print("\n" + "=" * 75)
    print("BALANCED DATASET VERIFICATION")
    print("=" * 75)

    print(f"Output file : {OUTPUT_FILE}")
    print(f"Rows        : {len(balanced_df):,}")
    print(f"Columns     : {len(balanced_df.columns)}")

    if OUTPUT_FILE.exists():
        file_size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
        print(f"Output size : {file_size_mb:.2f} MB")

    print("\nFinal label counts:")
    print(balanced_counts.to_string())

    # ---------------------------------------------------------------------
    # SAMPLE
    # ---------------------------------------------------------------------

    print("\n" + "=" * 75)
    print("BALANCED DATA SAMPLE")
    print("=" * 75)

    sample_columns = [
        "timestamp",
        "ip",
        "label",
        "requests_per_ip",
        "time_between_requests",
        "is_scanner",
        "is_bot",
        "is_browser",
        "high_volume_ip",
        "automated_activity"
    ]

    available_columns = [
        col for col in sample_columns
        if col in balanced_df.columns
    ]

    print(
        balanced_df[available_columns]
        .head(10)
        .to_string(index=False)
    )

    # ---------------------------------------------------------------------
    # REPORT
    # ---------------------------------------------------------------------

    report_lines = []

    report_lines.append("=" * 75)
    report_lines.append("PRACTICAL 6 - DATASET BALANCING REPORT")
    report_lines.append("=" * 75)
    report_lines.append("")

    report_lines.append("INPUT DATASET")
    report_lines.append("-" * 75)
    report_lines.append(f"Input file: {INPUT_FILE}")
    report_lines.append(f"Input rows: {len(df):,}")
    report_lines.append(f"Input columns: {len(df.columns)}")
    report_lines.append("")

    report_lines.append("ORIGINAL CLASS DISTRIBUTION")
    report_lines.append("-" * 75)

    for label, count in original_counts.items():
        percentage = original_percent[label]
        report_lines.append(
            f"{label:<15} {count:>12,} ({percentage:.2f}%)"
        )

    report_lines.append("")

    report_lines.append("BALANCING METHOD")
    report_lines.append("-" * 75)
    report_lines.append("Controlled Random Undersampling")
    report_lines.append(f"Random state: {RANDOM_STATE}")
    report_lines.append(
        f"Target samples per class: {min_class_count:,}"
    )
    report_lines.append("")

    report_lines.append("BALANCED CLASS DISTRIBUTION")
    report_lines.append("-" * 75)

    for label, count in balanced_counts.items():
        percentage = balanced_percent[label]
        report_lines.append(
            f"{label:<15} {count:>12,} ({percentage:.2f}%)"
        )

    report_lines.append("")

    report_lines.append("OUTPUT DATASET")
    report_lines.append("-" * 75)
    report_lines.append(f"Output file: {OUTPUT_FILE}")
    report_lines.append(f"Output rows: {len(balanced_df):,}")
    report_lines.append(f"Output columns: {len(balanced_df.columns)}")

    if OUTPUT_FILE.exists():
        report_lines.append(
            f"Output size: "
            f"{OUTPUT_FILE.stat().st_size / (1024 * 1024):.2f} MB"
        )

    report_lines.append("")

    report_lines.append("OBSERVATION")
    report_lines.append("-" * 75)
    report_lines.append(
        "The original dataset was highly imbalanced."
    )
    report_lines.append(
        "Controlled random undersampling was used to give every "
        "class equal representation."
    )
    report_lines.append(
        "The balanced dataset is intended for subsequent machine "
        "learning experiments."
    )

    save_report(report_lines)

    print("\nReport saved to:")
    print(REPORT_FILE)

    print("\n" + "=" * 75)
    print("PRACTICAL 6 COMPLETED SUCCESSFULLY")
    print("=" * 75)


if __name__ == "__main__":
    main()