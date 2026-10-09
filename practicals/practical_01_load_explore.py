"""
Practical 1: Load and Explore the Unstructured Access Log Data

Dataset:
    Data/raw/cj.log

Objective:
    Load and explore the raw semi-structured access log data.
"""

import json
from pathlib import Path
from collections import Counter


# ============================================================
# 1. CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "Data" / "raw" / "cj.log"

print("=" * 70)
print("PRACTICAL 1 - LOAD AND EXPLORE ACCESS LOG DATA")
print("=" * 70)

print(f"\nLog file: {LOG_FILE}")


# ============================================================
# 2. CHECK WHETHER FILE EXISTS
# ============================================================

if not LOG_FILE.exists():
    print("\nERROR: cj.log file was not found.")
    print(f"Expected location: {LOG_FILE}")
    raise FileNotFoundError(LOG_FILE)

print("File status: FOUND")


# ============================================================
# 3. FILE INFORMATION
# ============================================================

file_size_bytes = LOG_FILE.stat().st_size
file_size_mb = file_size_bytes / (1024 * 1024)

print("\n" + "-" * 70)
print("FILE INFORMATION")
print("-" * 70)

print(f"File name       : {LOG_FILE.name}")
print(f"File size       : {file_size_mb:.2f} MB")


# ============================================================
# 4. COUNT TOTAL RECORDS
# ============================================================

print("\nCounting records...")

total_records = 0

with LOG_FILE.open("r", encoding="utf-8", errors="replace") as file:
    for line in file:
        if line.strip():
            total_records += 1

print(f"Total log records: {total_records:,}")


# ============================================================
# 5. READ FIRST 10 RAW RECORDS
# ============================================================

print("\n" + "-" * 70)
print("FIRST 10 RAW RECORDS")
print("-" * 70)

with LOG_FILE.open("r", encoding="utf-8", errors="replace") as file:

    for i in range(10):

        line = file.readline()

        if not line:
            break

        print(f"\nRecord {i + 1}:")
        print(line.strip())


# ============================================================
# 6. PARSE FIRST RECORD TO UNDERSTAND STRUCTURE
# ============================================================

print("\n" + "-" * 70)
print("RAW RECORD STRUCTURE")
print("-" * 70)

with LOG_FILE.open("r", encoding="utf-8", errors="replace") as file:

    first_line = file.readline().strip()

try:

    first_record = json.loads(first_line)

    print("\nFirst record parsed successfully.")
    print(f"Record type : {type(first_record).__name__}")
    print(f"Number of fields: {len(first_record)}")

    for index, value in enumerate(first_record):

        print(
            f"Field {index}: "
            f"value={value!r}, "
            f"type={type(value).__name__}"
        )

except json.JSONDecodeError as error:

    print("\nERROR: First record could not be parsed as JSON.")
    print(error)


# ============================================================
# 7. DEFINE EXPECTED FIELD MEANINGS
# ============================================================

print("\n" + "-" * 70)
print("IDENTIFIED FIELDS")
print("-" * 70)

field_names = {
    0: "unused_field_1",
    1: "unused_field_2",
    2: "timestamp",
    3: "ip",
    4: "port",
    5: "user_agent",
    6: "language",
    7: "metadata"
}

for index, name in field_names.items():
    print(f"Field {index}: {name}")


# ============================================================
# 8. SAMPLE DATA EXPLORATION
# ============================================================

print("\n" + "-" * 70)
print("SAMPLE DATA EXPLORATION")
print("-" * 70)

sample_records = []

with LOG_FILE.open("r", encoding="utf-8", errors="replace") as file:

    for line in file:

        line = line.strip()

        if not line:
            continue

        try:

            record = json.loads(line)

            if isinstance(record, list):
                sample_records.append(record)

        except json.JSONDecodeError:
            continue

        if len(sample_records) >= 100:
            break


print(f"Valid sample records loaded: {len(sample_records)}")


# ============================================================
# 9. MISSING VALUE ANALYSIS
# ============================================================

print("\n" + "-" * 70)
print("MISSING VALUE ANALYSIS - SAMPLE")
print("-" * 70)

missing_counts = Counter()

for record in sample_records:

    for index, value in enumerate(record):

        if value is None:
            missing_counts[field_names.get(index, f"field_{index}")] += 1


for field, count in missing_counts.items():

    print(f"{field:20s}: {count}")


# ============================================================
# 10. UNIQUE IP ANALYSIS - SAMPLE
# ============================================================

print("\n" + "-" * 70)
print("IP ADDRESS ANALYSIS - SAMPLE")
print("-" * 70)

ips = []

for record in sample_records:

    if len(record) > 3:

        ip = record[3]

        if ip is not None:
            ips.append(ip)


unique_ips = set(ips)

print(f"Total IP values in sample : {len(ips)}")
print(f"Unique IPs in sample       : {len(unique_ips)}")

print("\nTop IP addresses in sample:")

for ip, count in Counter(ips).most_common(10):

    print(f"{ip:20s} -> {count}")


# ============================================================
# 11. PORT ANALYSIS
# ============================================================

print("\n" + "-" * 70)
print("PORT ANALYSIS - SAMPLE")
print("-" * 70)

ports = []

for record in sample_records:

    if len(record) > 4:

        port = record[4]

        if port is not None:
            ports.append(port)


print(f"Total port values: {len(ports)}")
print(f"Unique ports     : {len(set(ports))}")

print("\nTop ports in sample:")

for port, count in Counter(ports).most_common(10):

    print(f"{port:10s} -> {count}")


# ============================================================
# 12. LANGUAGE ANALYSIS
# ============================================================

print("\n" + "-" * 70)
print("LANGUAGE ANALYSIS - SAMPLE")
print("-" * 70)

languages = []

for record in sample_records:

    if len(record) > 6:

        language = record[6]

        if language is not None:
            languages.append(language)


print(f"Total language values: {len(languages)}")
print(f"Unique languages     : {len(set(languages))}")

print("\nLanguage distribution:")

for language, count in Counter(languages).most_common(10):

    print(f"{language:10s} -> {count}")


# ============================================================
# 13. USER-AGENT ANALYSIS
# ============================================================

print("\n" + "-" * 70)
print("USER-AGENT ANALYSIS - SAMPLE")
print("-" * 70)

user_agents = []

for record in sample_records:

    if len(record) > 5:

        user_agent = record[5]

        if user_agent is not None:
            user_agents.append(user_agent)


print(f"Total user-agent values: {len(user_agents)}")
print(f"Unique user-agents     : {len(set(user_agents))}")

print("\nFirst 5 user-agents:")

for user_agent in list(dict.fromkeys(user_agents))[:5]:

    print(f"- {user_agent}")


# ============================================================
# 14. TIMESTAMP ANALYSIS
# ============================================================

print("\n" + "-" * 70)
print("TIMESTAMP ANALYSIS - SAMPLE")
print("-" * 70)

timestamps = []

for record in sample_records:

    if len(record) > 2:

        timestamp = record[2]

        if timestamp is not None:
            timestamps.append(timestamp)


print(f"Timestamp values: {len(timestamps)}")

if timestamps:

    print(f"First timestamp in sample : {min(timestamps)}")
    print(f"Last timestamp in sample  : {max(timestamps)}")


# ============================================================
# 15. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("PRACTICAL 1 SUMMARY")
print("=" * 70)

print(f"Total records       : {total_records:,}")
print(f"File size           : {file_size_mb:.2f} MB")
print(f"Sample records      : {len(sample_records)}")
print(f"Unique sample IPs   : {len(unique_ips)}")
print(f"Unique sample ports : {len(set(ports))}")
print(f"Unique languages    : {len(set(languages))}")
print(f"Unique user-agents  : {len(set(user_agents))}")

print("\nPractical 1 completed successfully.")
print("=" * 70)