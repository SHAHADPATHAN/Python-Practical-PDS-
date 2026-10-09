"""
Report and practical solution service — reads from practicals/, outputs/reports/ and outputs/figures/.
Provides complete practical-wise solution guides, source codes, execution outputs, and viva Q&A.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.utils import paths


PRACTICAL_SOLUTIONS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Load & Explore Raw Access Logs",
        "objective": "Load and inspect large-scale semi-structured access log data without memory exhaustion.",
        "aim": "To load, parse line-by-line, and analyze the structural integrity of the raw cj.log file, identifying schema consistency, line counts, and JSON format anomalies.",
        "theory": (
            "Server access logs are typically generated in streaming append-only formats. Large logs (200+ MB) cannot "
            "always be loaded into memory at once with standard json.loads(). A streaming file iterator with buffered "
            "line-by-line inspection is used. In this dataset, records are formatted as JSON array representations "
            "[timestamp, ip, port, method, path, response_code, packet_size, user_agent]."
        ),
        "steps": [
            "Verify file existence and verify total size on disk using pathlib.Path.stat().",
            "Implement a buffered line generator to count total lines without loading entire file into RAM.",
            "Inspect sample records from the beginning, middle, and end of the dataset.",
            "Check for malformed JSON lines, trailing commas, and unescaped quote characters.",
            "Calculate summary metrics: valid lines, blank lines, and average line byte lengths."
        ],
        "input": "Data/raw/cj.log",
        "output": "Console summary output",
        "script": "practical_01_load_explore.py",
        "report_key": None,
        "key_result": "2,061,431 non-empty records found in a 215.4 MB raw file; average line length ~109 bytes.",
        "viva_questions": [
            {
                "q": "Why is streaming line-by-line processing preferred over json.load() for cj.log?",
                "a": "cj.log is 215 MB containing 2.06M lines. Using json.load() on the entire file would require converting it to an enormous Python in-memory list, causing memory spikes and potential Out-Of-Memory (OOM) errors. Streaming line-by-line requires only O(1) memory."
            },
            {
                "q": "What data format is used inside each line of cj.log?",
                "a": "Each line represents a JSON array with heterogeneous fields: string timestamps, IPv4 addresses, integer ports, HTTP request strings, status codes, packet sizes, and user agent strings."
            }
        ]
    },
    {
        "id": 2,
        "title": "Parse & Structure Semi-Structured Logs",
        "objective": "Convert raw semi-structured JSON array records into a clean, normalized relational CSV dataset.",
        "aim": "To construct an automated parsing engine with robust exception handling that extracts JSON tokens, enforces a canonical schema, logs malformed lines, and exports structured_logs.csv.",
        "theory": (
            "Semi-structured logs must be flattened into tabular format (columns & rows) for machine learning. "
            "Parsing involves JSON deserialization with schema validation: validating array length, handling "
            "escaped quotes, null byte characters, and isolating invalid JSON lines into an error log."
        ),
        "steps": [
            "Define the canonical column schema: timestamp, ip, port, method, path, response_code, packet_size, user_agent.",
            "Use chunked reading (100,000 lines per chunk) to process the 2.06 million lines smoothly.",
            "Apply json.loads() with try-except fallback for malformed entries.",
            "Filter out and log malformed entries to an error counter.",
            "Convert parsed chunks into Pandas DataFrames and append to structured_logs.csv."
        ],
        "input": "Data/raw/cj.log",
        "output": "Data/processed/structured_logs.csv (157 MB)",
        "script": "practical_02_parse_structure.py",
        "report_key": "schema",
        "key_result": "2,060,520 valid records successfully parsed; 911 invalid JSON lines safely trapped and documented.",
        "viva_questions": [
            {
                "q": "What caused the 911 invalid lines in cj.log?",
                "a": "Malformed payload injections, unescaped double quotes inside User-Agent strings, and interrupted log writes during server shutdown."
            },
            {
                "q": "What is the benefit of saving intermediate structured_logs.csv?",
                "a": "Decouples syntactic parsing from downstream preprocessing. Downstream practicals can read CSV directly using optimized column projection instead of repeatedly parsing raw JSON."
            }
        ]
    },
    {
        "id": 3,
        "title": "Clean & Preprocess Log Records",
        "objective": "Validate, normalize, and sanitize timestamps, network endpoints, and text strings.",
        "aim": "To perform comprehensive data cleaning on structured_logs.csv including timestamp parsing to UTC, IP address format validation, port number range checks, and user-agent normalization.",
        "theory": (
            "Data preprocessing guarantees data hygiene before modeling. Key tasks: datetime parsing converts "
            "human-readable timestamps into UNIX epoch or UTC datetime objects. Network validation ensures IPs follow "
            "IPv4 dotted-decimal syntax (0-255 octets) and ports fall in the valid range [1, 65535]. Text normalization "
            "lowercases HTTP verbs and strips unprintable control characters."
        ),
        "steps": [
            "Parse timestamp strings to pd.to_datetime with UTC timezone normalization.",
            "Validate IP addresses using regex ^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$ and check valid octet ranges (0-255).",
            "Validate network ports ensuring 1 <= port <= 65535, identifying standard vs ephemeral ports.",
            "Normalize HTTP methods (GET, POST, HEAD, PUT, OPTIONS) and handle missing/empty values.",
            "Clean and sanitize user-agent strings, replacing empty or whitespace-only values with 'unknown'.",
            "Export cleaned dataset to cleaned_logs.csv."
        ],
        "input": "Data/processed/structured_logs.csv",
        "output": "Data/processed/cleaned_logs.csv (235 MB)",
        "script": "practical_03_clean_preprocess.py",
        "report_key": "cleaning",
        "key_result": "Zero missing timestamps, 100% valid IPv4 addresses, text fields normalized, saved cleaned_logs.csv.",
        "viva_questions": [
            {
                "q": "Why is timestamp conversion to standard datetime64 crucial for log analysis?",
                "a": "Datetime objects allow vectorised date/time arithmetic, extraction of temporal components (hour, day of week), time-series resampling, and computation of inter-arrival deltas between requests."
            },
            {
                "q": "How were missing User-Agent strings treated?",
                "a": "Instead of dropping rows, missing User-Agents were flagged with a boolean indicator 'user_agent_missing=True' and replaced with 'unknown', preserving volume telemetry."
            }
        ]
    },
    {
        "id": 4,
        "title": "Rule-Based Threat & Attack Labeling",
        "objective": "Classify log records into security categories: benign, bot, scanner, or suspicious.",
        "aim": "To establish ground-truth security labels across 2,060,520 records using domain-driven heuristic rules, signature dictionaries (Gobuster, DirBuster, Nmap, Nikto), and behavioral indicators.",
        "theory": (
            "Supervised machine learning requires ground truth. Since raw logs lack labels, security domain rules "
            "are formulated: (1) Scanner: User-agent matching security fuzzer keywords (Gobuster, DirBuster, Nikto, Nmap). "
            "(2) Bot: Automation libraries (python-requests, go-http-client, curl, spiders). "
            "(3) Suspicious: High-frequency rapid requests (<1s interval) without explicit scanner signatures. "
            "(4) Benign: Legitimate browsers (Chrome, Firefox, Safari) with normal human traversal."
        ),
        "steps": [
            "Compile signature dictionaries for directory scanners and automated bots.",
            "Extract keywords from the normalized user_agent column using regex pattern matching.",
            "Classify scanner tools: gobuster, dirbuster, nmap, nikto, masscan, wpscan, zgrab.",
            "Classify bot clients: python-requests, go-http-client, curl, spider, crawler.",
            "Apply temporal rate heuristics to label rapid repeated probes as 'suspicious'.",
            "Assign default label 'benign' to human browser sessions.",
            "Export ground truth dataset to labeled_logs.csv."
        ],
        "input": "Data/processed/cleaned_logs.csv",
        "output": "Data/processed/labeled_logs.csv (307 MB)",
        "script": "practical_04_label_attacks.py",
        "report_key": "labeling",
        "key_result": "scanner: 1,827,367 (88.68%) | suspicious: 167,486 (8.13%) | benign: 61,091 (2.96%) | bot: 4,576 (0.22%).",
        "viva_questions": [
            {
                "q": "Why are scanners the vast majority (88.68%) of the dataset?",
                "a": "Automated directory fuzzers like Gobuster and DirBuster send thousands of automated dictionary requests per minute, massively inflating their volume relative to human users."
            },
            {
                "q": "Is rule-based labeling 100% accurate in real-world security?",
                "a": "No, sophisticated attackers can spoof user-agent strings (e.g. masquerading as Chrome). That is why behavioral feature engineering (Practical 05) is necessary."
            }
        ]
    },
    {
        "id": 5,
        "title": "Comprehensive Feature Engineering",
        "objective": "Engineer 33+ predictive features capturing temporal, behavioral, lexical, and interaction signals.",
        "aim": "To transform raw log attributes into a high-dimensional feature matrix for ML, encoding cyclical time, IP burst rates, Shannon entropy, and interaction flags.",
        "theory": (
            "Raw logs contain strings and timestamps that ML algorithms cannot digest directly. Feature engineering "
            "extracts numerical patterns: (1) Cyclical time: hour_sin = sin(2*pi*hour/24), hour_cos = cos(2*pi*hour/24). "
            "(2) Behavioral: requests_per_ip_hour, requests_per_ip_minute, unique_ports_per_ip. "
            "(3) Lexical Entropy: Shannon entropy H = -sum(p * log2(p)) measuring randomness in User-Agents. "
            "(4) Anomalies: rapid_request_1s (delta < 1s), rapid_and_high_volume."
        ),
        "steps": [
            "Extract temporal features: hour, minute, day_of_week, is_weekend.",
            "Compute cyclical trigonometric transformations: hour_sin and hour_cos.",
            "Calculate client IP frequency aggregations: requests_per_ip, requests_per_ip_hour, requests_per_ip_minute.",
            "Calculate IP diversity metrics: unique_ports_per_ip, unique_paths_per_ip.",
            "Compute lexical metrics: user_agent_length and user_agent_entropy (Shannon entropy).",
            "Derive binary interaction flags: rapid_request_1s, scanner_and_high_volume, rapid_and_high_volume.",
            "Export full feature store to features.csv (746 MB)."
        ],
        "input": "Data/processed/labeled_logs.csv",
        "output": "Data/processed/features.csv (746 MB)",
        "script": "practical_05_feature_engineering.py",
        "report_key": "features",
        "key_result": "33 multi-dimensional numerical & categorical features successfully engineered.",
        "viva_questions": [
            {
                "q": "Why use cyclical sin/cos encoding for the hour feature?",
                "a": "Hours wrap around continuously: hour 23 (23:00) and hour 0 (00:00) are 1 hour apart, but numerically |23 - 0| = 23. Sin/cos maps them onto a continuous unit circle where 23:00 and 00:00 are adjacent."
            },
            {
                "q": "What does high Shannon entropy in a user-agent indicate?",
                "a": "Legitimate browsers have structured, predictable substrings. Attackers using randomized token generators or automated fuzzers often produce high-entropy strings."
            }
        ]
    },
    {
        "id": 6,
        "title": "Class Imbalance & Data Balancing",
        "objective": "Resolve severe class skew (400:1) to prevent classifier majority-class bias.",
        "aim": "To evaluate balancing strategies, justify stratified random undersampling, and create balanced_logs.csv with equal representation (4,576 records per class).",
        "theory": (
            "When one class represents 88.68% and another 0.22%, standard classifiers achieve high accuracy by simply "
            "guessing the majority class ('Accuracy Paradox'). In security, minority classes (bots, stealth attacks) are "
            "the most critical. Stratified undersampling downsamples majority classes to match the minority anchor "
            "(4,576 bot samples), producing equal 25% class balance without synthetic interpolation artifacts."
        ),
        "steps": [
            "Compute class frequencies and visualize the 400:1 distribution skew.",
            "Evaluate techniques: Random Undersampling vs SMOTE vs Class Weights.",
            "Anchor sampling size at minority class count N = 4,576 (Bot class).",
            "Perform stratified random sampling without replacement using random_state=42 for reproducibility.",
            "Verify equal balance: 4,576 scanner, 4,576 suspicious, 4,576 benign, 4,576 bot (18,304 total).",
            "Export balanced dataset to balanced_logs.csv."
        ],
        "input": "Data/processed/features.csv",
        "output": "Data/processed/balanced_logs.csv (6.97 MB)",
        "script": "practical_06_balancing.py",
        "report_key": "balancing",
        "key_result": "18,304 balanced records generated (4,576 per class); dataset size reduced from 746 MB to 6.97 MB.",
        "viva_questions": [
            {
                "q": "Why was undersampling chosen over SMOTE (Synthetic Minority Over-sampling)?",
                "a": "SMOTE generates synthetic interpolations in feature space. In network security, discrete user-agent flags and categorical tool indicators cannot be syntactically averaged without creating invalid artifacts."
            },
            {
                "q": "What is the tradeoff of undersampling 1.8M scanner records to 4,576?",
                "a": "Information loss: we discard 99.7% of redundant scanner records. However, because scanner records are highly repetitive, 4,576 samples capture the statistical distribution with 100x faster training."
            }
        ]
    },
    {
        "id": 7,
        "title": "Data Wrangling & Multidimensional Aggregation",
        "objective": "Transform balanced logs into summary tables, pivots, and targeted analytical slices.",
        "aim": "To construct aggregated IP behavioral profiles, hourly time-series resamplings, 24-hr label cross-tabulations, and filter targeted threat sub-cohorts using Pandas.",
        "theory": (
            "Data wrangling reorganizes clean data into decision-support structures. Key operations: "
            "(1) GroupBy aggregation produces host summaries (total requests, unique ports, active duration). "
            "(2) Temporal resampling groups timestamp data into 1-hour bins to track diurnal volume shifts. "
            "(3) Pivot tables cross-tabulate two categorical dimensions (Hour x Label) to analyze temporal threat shifts. "
            "(4) Boolean masking isolates internal vs external network cohorts."
        ),
        "steps": [
            "Group by IP address and aggregate request counts, first/last seen, and port counts into ip_summary.csv.",
            "Resample time series at 1-hour frequency into hourly_activity.csv.",
            "Construct a 24x4 cross-tabulation pivot table into label_hour_pivot.csv.",
            "Apply subnet filters for internal IPs (10.x, 192.168.x) and bot traffic into filtered_activity.csv.",
            "Document insights on host behavioral persistence and nocturnal threat trends."
        ],
        "input": "Data/processed/balanced_logs.csv",
        "output": "ip_summary.csv, hourly_activity.csv, label_hour_pivot.csv, filtered_activity.csv",
        "script": "practical_07_data_wrangling.py",
        "report_key": "wrangling",
        "key_result": "Four specialized analytical tables created; identified peak scanning hours (08:00 - 16:00 UTC).",
        "viva_questions": [
            {
                "q": "What did the label_hour_pivot reveal about bot traffic compared to scanners?",
                "a": "Scanners exhibit sharp diurnal peaks between 08:00 and 16:00 UTC, while bot traffic is uniformly distributed 24 hours a day with zero nocturnal drop-off."
            },
            {
                "q": "How was active host duration calculated?",
                "a": "active_duration_seconds = (max(timestamp) - min(timestamp)).total_seconds() for each distinct IP address."
            }
        ]
    },
    {
        "id": 8,
        "title": "Exploratory Data Analysis (EDA) & Visualization",
        "objective": "Visualize temporal dynamics, threat concentrations, and host distributions.",
        "aim": "To produce 8 publication-grade analytical figures exploring label distribution, request timelines, hourly patterns, top IPs, and correlation heatmaps using Matplotlib and Seaborn.",
        "theory": (
            "Visual EDA converts tabular statistical summaries into intuitive visual representations. "
            "Key visualizations include: bar charts for discrete distributions, line curves for temporal trends, "
            "horizontal rankings for top IPs, and 2D heatmaps with continuous color scales for temporal density."
        ),
        "steps": [
            "Configure Matplotlib and Seaborn dark cybersecurity theme styling.",
            "Generate Figure 01: Overall Attack Label Distribution (Donut Chart).",
            "Generate Figure 02: Total Requests Over Time (Continuous Timeline).",
            "Generate Figure 03: Hourly Request Aggregation (24-Hour Diurnal Bar Chart).",
            "Generate Figure 04: Top 10 IP Addresses by Request Count.",
            "Generate Figure 05: Attack Category Shift Over Time.",
            "Generate Figure 06: 24-Hour Hourly Label Density Heatmap.",
            "Generate Figure 07: High-Frequency Scanner IP Comparison.",
            "Generate Figure 08: Bot vs Internal Network Activity Profile.",
            "Save all 8 publication PNG figures in outputs/figures/."
        ],
        "input": "Data/processed/balanced_logs.csv",
        "output": "outputs/figures/ (8 high-resolution PNG charts)",
        "script": "practical_08_eda.py",
        "report_key": "eda",
        "key_result": "8 high-resolution figures generated documenting peak diurnal bursts and IP threat concentrations.",
        "viva_questions": [
            {
                "q": "Why is a heatmap effective for displaying the hour-by-label matrix?",
                "a": "A 2D color matrix immediately highlights high-density clusters (bright cells during 08:00-16:00 for scanners) without cluttering the screen with 24 individual bar charts."
            },
            {
                "q": "What was the date of peak traffic discovered during EDA?",
                "a": "January 18, 2024, which experienced an intense concentrated burst of directory brute-force fuzzing."
            }
        ]
    },
    {
        "id": 9,
        "title": "Machine Learning Attack Classification",
        "objective": "Train, evaluate, and critically reflect on a multi-class Random Forest classifier.",
        "aim": "To train a 200-tree Random Forest classifier on balanced features, evaluate precision, recall, and F1 across all 4 classes, and conduct a scientific investigation into potential feature leakage.",
        "theory": (
            "Random Forest is an ensemble learning method combining multiple de-correlated decision trees trained on "
            "random subsets of data and features. It minimizes overfitting and outputs Gini feature importances. "
            "Evaluation uses a held-out test split (20%) measuring Precision (TP/(TP+FP)), Recall (TP/(TP+FN)), and F1. "
            "Critical reflection: if features contain direct hints from the labeling heuristics, evaluation accuracy "
            "will be artificially inflated (Label Leakage)."
        ),
        "steps": [
            "Encode labels (benign, bot, scanner, suspicious) using LabelEncoder.",
            "Partition data into 80% training (14,643 rows) and 20% test (3,661 rows) using stratified train_test_split.",
            "Configure RandomForestClassifier(n_estimators=200, max_depth=20, min_samples_split=4, class_weight='balanced', random_state=42).",
            "Fit the model on training split and predict test set labels.",
            "Compute Confusion Matrix, Precision (0.9923), Recall (0.9921), and Macro F1 (0.9921).",
            "Calculate Gini feature importances and rank the top 15 predictive signals.",
            "Analyze and document potential data leakage from bot_indicator_none and scanner_indicator_none.",
            "Serialize trained model package (model, encoder, columns) to models/random_forest_classifier.joblib."
        ],
        "input": "Data/processed/balanced_logs.csv",
        "output": "models/random_forest_classifier.joblib (3.55 MB)",
        "script": "practical_09_classifier.py",
        "report_key": "classifier",
        "key_result": "Accuracy 99.21%, Macro F1 99.21%; identified and documented feature leakage from rule-based indicators.",
        "viva_questions": [
            {
                "q": "Why does the model achieve 99.21% accuracy, and why is this flagged in the report?",
                "a": "bot_indicator_none and scanner_indicator_none carry 11.2% combined importance and were derived from the same keywords used in Practical 04 labeling. This constitutes partial label leakage, so the 99.21% accuracy reflects rule reconstruction rather than pure generalized threat detection."
            },
            {
                "q": "How would you eliminate this leakage in a production deployment?",
                "a": "Remove all indicator features and train the classifier exclusively on pure behavioral and statistical metrics: requests_per_ip_hour, user_agent_entropy, rapid_request_1s, and unique_ports_per_ip."
            }
        ]
    },
    {
        "id": 10,
        "title": "Reusable End-to-End Production Pipeline",
        "objective": "Build a modular, class-based log intelligence pipeline for automated inference.",
        "aim": "To architect an object-oriented Python pipeline (LogAnalyticsPipeline) that automates the complete lifecycle: raw log ingestion -> parsing -> cleaning -> threat labeling -> feature engineering -> feature export.",
        "theory": (
            "In data science, transitioning from exploratory code to production requires modular encapsulation. "
            "A reusable pipeline bundles all transformation steps into standardized classes with fit() and transform() "
            "interfaces, supporting configuration parameters, robust logging, exception handling, and standardized exports."
        ),
        "steps": [
            "Design LogAnalyticsPipeline class with modular methods for each transformation stage.",
            "Implement automated log format detection supporting CJ, Apache, and standard server logs.",
            "Integrate automated timestamp cleaning and IPv4 validation pipelines.",
            "Integrate rule-based labeling heuristic engine.",
            "Execute feature extraction generating all 33 behavioral and temporal variables.",
            "Run end-to-end verification and export outputs to pipeline_features.csv.",
            "Generate practical_10_pipeline_report.txt confirming 100% pipeline completion."
        ],
        "input": "Data/raw/cj.log",
        "output": "Data/processed/pipeline_features.csv (~6.8 MB)",
        "script": "practical_10_pipeline.py",
        "report_key": "pipeline",
        "key_result": "Complete reusable object-oriented pipeline constructed and validated against the full dataset.",
        "viva_questions": [
            {
                "q": "What is the primary architectural advantage of the Practical 10 pipeline?",
                "a": "It replaces 10 standalone sequential scripts with a single unified, reproducible module that can ingest any new log file and immediately produce clean, labeled ML-ready features."
            },
            {
                "q": "How does this pipeline connect with the web dashboard backend?",
                "a": "The FastAPI backend upload endpoint (/api/upload) calls this pipeline logic directly to parse, label, and extract features from files uploaded by users in real time."
            }
        ]
    }
]


def get_all_practicals() -> List[Dict[str, Any]]:
    result = []
    for p in PRACTICAL_SOLUTIONS:
        entry = dict(p)
        rk = p.get("report_key")
        if rk and rk in paths.REPORTS:
            entry["report_available"] = paths.REPORTS[rk].exists()
        else:
            entry["report_available"] = False
        
        script_file = paths.PRACTICALS_DIR / p["script"]
        entry["script_available"] = script_file.exists()
        result.append(entry)
    return result


def get_practical(pid: int) -> Optional[Dict[str, Any]]:
    meta = next((p for p in PRACTICAL_SOLUTIONS if p["id"] == pid), None)
    if not meta:
        return None
    entry = dict(meta)

    # Load Report Content
    rk = meta.get("report_key")
    if rk and rk in paths.REPORTS and paths.REPORTS[rk].exists():
        entry["report_content"] = paths.REPORTS[rk].read_text(
            encoding="utf-8", errors="replace"
        )
        entry["report_available"] = True
    else:
        entry["report_available"] = False

    # Load Python Script Content
    script_path = paths.PRACTICALS_DIR / meta["script"]
    if script_path.exists():
        entry["script_content"] = script_path.read_text(
            encoding="utf-8", errors="replace"
        )
        entry["script_available"] = True
    else:
        entry["script_content"] = None
        entry["script_available"] = False

    return entry


def get_all_reports() -> List[Dict[str, Any]]:
    result = []
    for key, path in paths.REPORTS.items():
        result.append({
            "key":        key,
            "filename":   path.name,
            "available":  path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else 0,
        })
    return result


def get_report(key: str) -> Optional[Dict[str, Any]]:
    if key not in paths.REPORTS:
        return None
    path = paths.REPORTS[key]
    if not path.exists():
        return {"key": key, "available": False, "content": None}
    return {
        "key":        key,
        "filename":   path.name,
        "available":  True,
        "content":    path.read_text(encoding="utf-8", errors="replace"),
        "size_bytes": path.stat().st_size,
    }
