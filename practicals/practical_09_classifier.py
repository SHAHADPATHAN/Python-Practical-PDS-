"""
===========================================================================
PRACTICAL 9 - BUILD CLASSIFIER
Python for Data Science
===========================================================================

Aim:
    Build and evaluate a Random Forest classifier for web-log
    activity classification.

Input:
    Data/processed/balanced_logs.csv

Classes:
    benign
    suspicious
    bot
    scanner

Outputs:
    models/random_forest_classifier.joblib
    outputs/figures/09_confusion_matrix.png
    outputs/reports/practical_09_classifier_report.txt
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score
)


# =========================================================================
# CONFIGURATION
# =========================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR /
    "Data" /
    "processed" /
    "balanced_logs.csv"
)

MODEL_DIR = BASE_DIR / "models"
FIGURE_DIR = BASE_DIR / "outputs" / "figures"
REPORT_DIR = BASE_DIR / "outputs" / "reports"

MODEL_FILE = (
    MODEL_DIR /
    "random_forest_classifier.joblib"
)

CONFUSION_MATRIX_FILE = (
    FIGURE_DIR /
    "09_confusion_matrix.png"
)

REPORT_FILE = (
    REPORT_DIR /
    "practical_09_classifier_report.txt"
)

RANDOM_STATE = 42
TEST_SIZE = 0.20


# =========================================================================
# DIRECTORY SETUP
# =========================================================================

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

FIGURE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================================
# MAIN
# =========================================================================

def main():

    print("=" * 75)
    print("PRACTICAL 9 - BUILD CLASSIFIER")
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

    if "label" not in df.columns:
        print("ERROR: Label column not found.")
        return

    # =====================================================================
    # TARGET
    # =====================================================================

    print("\n" + "=" * 75)
    print("TARGET VARIABLE")
    print("=" * 75)

    y_text = (
        df["label"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    print(
        y_text.value_counts().to_string()
    )

    # =====================================================================
    # REMOVE LEAKAGE-PRONE FEATURES
    # =====================================================================

    print("\n" + "=" * 75)
    print("FEATURE SELECTION")
    print("=" * 75)

    excluded_columns = [
        # Target
        "label",

        # Directly related to the labeling rules
        "scanner_type",
        "bot_type",
        "is_scanner",
        "is_bot",
        "automated_activity",

        # Raw identifiers
        "ip",

        # Raw timestamp will be represented through calendar features
        "timestamp",

        # Helper columns if present
        "date",
        "day",
        "hour_timestamp",
        "is_internal_ip"
    ]

    available_excluded = [
        col
        for col in excluded_columns
        if col in df.columns
    ]

    print("\nExcluded columns:")

    for col in available_excluded:
        print(f" - {col}")

    X = df.drop(
        columns=available_excluded,
        errors="ignore"
    ).copy()

    # =====================================================================
    # HANDLE CATEGORICAL FEATURES
    # =====================================================================

    print("\nPreparing feature matrix...")

    categorical_columns = X.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    numeric_columns = X.select_dtypes(
        include=[np.number, "bool"]
    ).columns.tolist()

    print(
        f"Numeric features     : "
        f"{len(numeric_columns)}"
    )

    print(
        f"Categorical features : "
        f"{len(categorical_columns)}"
    )

    if categorical_columns:

        print("\nCategorical columns:")

        for col in categorical_columns:
            print(f" - {col}")

        X = pd.get_dummies(
            X,
            columns=categorical_columns,
            dummy_na=True
        )

    # =====================================================================
    # CLEAN NUMERIC DATA
    # =====================================================================

    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    )

    X = X.fillna(0)

    # Convert Boolean columns to integer
    bool_columns = X.select_dtypes(
        include=["bool"]
    ).columns

    if len(bool_columns) > 0:

        X[bool_columns] = (
            X[bool_columns]
            .astype(int)
        )

    # Ensure all values are numeric
    X = X.apply(
        pd.to_numeric,
        errors="coerce"
    )

    X = X.fillna(0)

    print(
        f"\nFinal feature count: "
        f"{X.shape[1]}"
    )

    print(
        f"Feature matrix shape: "
        f"{X.shape}"
    )

    # =====================================================================
    # LABEL ENCODING
    # =====================================================================

    print("\nEncoding target labels...")

    label_encoder = LabelEncoder()

    y = label_encoder.fit_transform(
        y_text
    )

    print("\nClass encoding:")

    for index, label in enumerate(
        label_encoder.classes_
    ):
        print(
            f"{index} -> {label}"
        )

    # =====================================================================
    # TRAIN / TEST SPLIT
    # =====================================================================

    print("\n" + "=" * 75)
    print("TRAIN / TEST SPLIT")
    print("=" * 75)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y
    )

    print(
        f"Training samples : "
        f"{len(X_train):,}"
    )

    print(
        f"Testing samples  : "
        f"{len(X_test):,}"
    )

    print(
        f"Test size        : "
        f"{TEST_SIZE * 100:.0f}%"
    )

    # =====================================================================
    # RANDOM FOREST
    # =====================================================================

    print("\n" + "=" * 75)
    print("TRAINING RANDOM FOREST")
    print("=" * 75)

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight="balanced"
    )

    print("Training model...")

    model.fit(
        X_train,
        y_train
    )

    print("Model training completed.")

    # =====================================================================
    # PREDICTION
    # =====================================================================

    print("\nGenerating predictions...")

    y_pred = model.predict(
        X_test
    )

    # =====================================================================
    # METRICS
    # =====================================================================

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    print("\n" + "=" * 75)
    print("MODEL PERFORMANCE")
    print("=" * 75)

    print(
        f"Accuracy          : "
        f"{accuracy:.4f} "
        f"({accuracy * 100:.2f}%)"
    )

    print(
        f"Weighted Precision : "
        f"{precision:.4f}"
    )

    print(
        f"Weighted Recall    : "
        f"{recall:.4f}"
    )

    print(
        f"Weighted F1-score  : "
        f"{f1:.4f}"
    )

    # =====================================================================
    # CLASSIFICATION REPORT
    # =====================================================================

    print("\n" + "=" * 75)
    print("CLASSIFICATION REPORT")
    print("=" * 75)

    class_report = classification_report(
        y_test,
        y_pred,
        target_names=label_encoder.classes_,
        zero_division=0
    )

    print(class_report)

    # =====================================================================
    # CONFUSION MATRIX
    # =====================================================================

    print("=" * 75)
    print("CONFUSION MATRIX")
    print("=" * 75)

    cm = confusion_matrix(
        y_test,
        y_pred
    )

    print(
        pd.DataFrame(
            cm,
            index=label_encoder.classes_,
            columns=label_encoder.classes_
        )
    )

    plt.figure(
        figsize=(9, 7)
    )

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        xticklabels=label_encoder.classes_,
        yticklabels=label_encoder.classes_
    )

    plt.title(
        "Random Forest Confusion Matrix"
    )

    plt.xlabel(
        "Predicted Label"
    )

    plt.ylabel(
        "Actual Label"
    )

    plt.tight_layout()

    plt.savefig(
        CONFUSION_MATRIX_FILE,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"\nConfusion matrix saved to:"
    )
    print(
        CONFUSION_MATRIX_FILE
    )

    # =====================================================================
    # FEATURE IMPORTANCE
    # =====================================================================

    print("\n" + "=" * 75)
    print("TOP 15 FEATURE IMPORTANCES")
    print("=" * 75)

    importance_df = pd.DataFrame(
        {
            "feature": X.columns,
            "importance": model.feature_importances_
        }
    )

    importance_df = importance_df.sort_values(
        "importance",
        ascending=False
    )

    print(
        importance_df
        .head(15)
        .to_string(index=False)
    )

    # =====================================================================
    # FEATURE IMPORTANCE FIGURE
    # =====================================================================

    top_features = (
        importance_df
        .head(15)
        .sort_values("importance")
    )

    plt.figure(
        figsize=(11, 8)
    )

    sns.barplot(
        data=top_features,
        x="importance",
        y="feature"
    )

    plt.title(
        "Top 15 Random Forest Feature Importances"
    )

    plt.xlabel(
        "Importance"
    )

    plt.ylabel(
        "Feature"
    )

    plt.tight_layout()

    importance_file = (
        FIGURE_DIR /
        "10_feature_importance.png"
    )

    plt.savefig(
        importance_file,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"\nFeature importance figure saved:"
    )
    print(
        importance_file
    )

    # =====================================================================
    # SAVE MODEL
    # =====================================================================

    print("\n" + "=" * 75)
    print("SAVING MODEL")
    print("=" * 75)

    model_package = {
        "model": model,
        "label_encoder": label_encoder,
        "feature_columns": X.columns.tolist(),
        "excluded_columns": available_excluded,
        "random_state": RANDOM_STATE
    }

    joblib.dump(
        model_package,
        MODEL_FILE
    )

    print(
        f"Model saved to:"
    )
    print(
        MODEL_FILE
    )

    # =====================================================================
    # SAVE REPORT
    # =====================================================================

    report = []

    report.append("=" * 75)
    report.append("PRACTICAL 9 - CLASSIFIER REPORT")
    report.append("=" * 75)
    report.append("")

    report.append("DATASET")
    report.append("-" * 75)
    report.append(
        f"Input file: {INPUT_FILE}"
    )
    report.append(
        f"Total records: {len(df):,}"
    )
    report.append(
        f"Training records: {len(X_train):,}"
    )
    report.append(
        f"Testing records: {len(X_test):,}"
    )
    report.append("")

    report.append("MODEL")
    report.append("-" * 75)
    report.append(
        "Algorithm: Random Forest Classifier"
    )
    report.append(
        "Number of trees: 200"
    )
    report.append(
        "Maximum depth: 20"
    )
    report.append(
        f"Random state: {RANDOM_STATE}"
    )
    report.append("")

    report.append("FEATURES")
    report.append("-" * 75)
    report.append(
        f"Final feature count: {X.shape[1]}"
    )

    report.append(
        "Direct label-derived features were excluded "
        "to reduce data leakage."
    )

    report.append("")

    report.append("PERFORMANCE")
    report.append("-" * 75)
    report.append(
        f"Accuracy: {accuracy:.4f} "
        f"({accuracy * 100:.2f}%)"
    )
    report.append(
        f"Weighted Precision: {precision:.4f}"
    )
    report.append(
        f"Weighted Recall: {recall:.4f}"
    )
    report.append(
        f"Weighted F1-score: {f1:.4f}"
    )

    report.append("")

    report.append("CLASSIFICATION REPORT")
    report.append("-" * 75)
    report.append(class_report)

    report.append("")

    report.append("CONFUSION MATRIX")
    report.append("-" * 75)

    report.append(
        pd.DataFrame(
            cm,
            index=label_encoder.classes_,
            columns=label_encoder.classes_
        ).to_string()
    )

    report.append("")

    report.append("TOP 15 FEATURES")
    report.append("-" * 75)

    report.append(
        importance_df
        .head(15)
        .to_string(index=False)
    )

    report.append("")

    report.append("OUTPUT FILES")
    report.append("-" * 75)
    report.append(
        f"Model: {MODEL_FILE}"
    )
    report.append(
        f"Confusion matrix: {CONFUSION_MATRIX_FILE}"
    )
    report.append(
        f"Feature importance: {importance_file}"
    )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "\n".join(report)
        )

    # =====================================================================
    # FINAL VERIFICATION
    # =====================================================================

    print("\n" + "=" * 75)
    print("OUTPUT VERIFICATION")
    print("=" * 75)

    files_to_check = [
        MODEL_FILE,
        CONFUSION_MATRIX_FILE,
        importance_file,
        REPORT_FILE
    ]

    for file in files_to_check:

        if file.exists():

            size_mb = (
                file.stat().st_size
                / (1024 * 1024)
            )

            print(
                f"{file.name:<40} "
                f"{size_mb:.2f} MB"
            )

        else:

            print(
                f"{file.name:<40} "
                f"NOT FOUND"
            )

    print("\nReport saved to:")
    print(REPORT_FILE)

    print("\n" + "=" * 75)
    print("PRACTICAL 9 COMPLETED SUCCESSFULLY")
    print("=" * 75)


# =========================================================================
# ENTRY POINT
# =========================================================================

if __name__ == "__main__":
    main()