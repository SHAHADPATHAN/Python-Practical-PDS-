"""
Centralised path configuration for the PDS Log Intelligence backend.
All paths are resolved relative to the project root.
"""

from pathlib import Path

# Project root  (backend/utils/paths.py -> backend -> project root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ─── Raw data ────────────────────────────────────────────────────────────────
RAW_DIR         = BASE_DIR / "Data" / "raw"
LOG_FILE        = RAW_DIR  / "cj.log"

# ─── Processed data ───────────────────────────────────────────────────────────
PROCESSED_DIR        = BASE_DIR / "Data" / "processed"
STRUCTURED_CSV       = PROCESSED_DIR / "structured_logs.csv"
CLEANED_CSV          = PROCESSED_DIR / "cleaned_logs.csv"
LABELED_CSV          = PROCESSED_DIR / "labeled_logs.csv"
FEATURES_CSV         = PROCESSED_DIR / "features.csv"
BALANCED_CSV         = PROCESSED_DIR / "balanced_logs.csv"
IP_SUMMARY_CSV       = PROCESSED_DIR / "ip_summary.csv"
HOURLY_CSV           = PROCESSED_DIR / "hourly_activity.csv"
PIVOT_CSV            = PROCESSED_DIR / "label_hour_pivot.csv"
FILTERED_CSV         = PROCESSED_DIR / "filtered_activity.csv"
PIPELINE_FEATURES    = PROCESSED_DIR / "pipeline_features.csv"

# ─── Models ───────────────────────────────────────────────────────────────────
MODEL_DIR  = BASE_DIR / "models"
MODEL_FILE = MODEL_DIR / "random_forest_classifier.joblib"

# ─── Outputs ──────────────────────────────────────────────────────────────────
FIGURES_DIR = BASE_DIR / "outputs" / "figures"
REPORTS_DIR = BASE_DIR / "outputs" / "reports"

# ─── Report files ─────────────────────────────────────────────────────────────
REPORTS = {
    "schema":      REPORTS_DIR / "practical_02_schema_report.txt",
    "cleaning":    REPORTS_DIR / "practical_03_cleaning_report.txt",
    "labeling":    REPORTS_DIR / "practical_04_labeling_report.txt",
    "features":    REPORTS_DIR / "practical_05_feature_report.txt",
    "balancing":   REPORTS_DIR / "practical_06_balancing_report.txt",
    "wrangling":   REPORTS_DIR / "practical_07_wrangling_report.txt",
    "eda":         REPORTS_DIR / "practical_08_eda_report.txt",
    "classifier":  REPORTS_DIR / "practical_09_classifier_report.txt",
    "pipeline":    REPORTS_DIR / "practical_10_pipeline_report.txt",
}

# ─── Figure files ─────────────────────────────────────────────────────────────
FIGURES = {
    "label_distribution":   FIGURES_DIR / "01_label_distribution.png",
    "requests_over_time":   FIGURES_DIR / "02_requests_over_time.png",
    "requests_by_hour":     FIGURES_DIR / "03_requests_by_hour.png",
    "top_10_ips":           FIGURES_DIR / "04_top_10_ips.png",
    "labels_over_time":     FIGURES_DIR / "05_labels_over_time.png",
    "hourly_heatmap":       FIGURES_DIR / "06_hourly_label_heatmap.png",
    "top_scanner_ips":      FIGURES_DIR / "07_top_scanner_ips.png",
    "bot_internal":         FIGURES_DIR / "08_bot_internal_activity.png",
    "confusion_matrix":     FIGURES_DIR / "09_confusion_matrix.png",
    "feature_importance":   FIGURES_DIR / "10_feature_importance.png",
}

# ─── Upload / temp ────────────────────────────────────────────────────────────
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ─── Practicals ───────────────────────────────────────────────────────────────
PRACTICALS_DIR = BASE_DIR / "practicals"
