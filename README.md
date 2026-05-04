# Alarm Discrepancy Tracker

## Overview

This project is a Python automation tool that compares current operational data against known reference data and generates a clean exception report for review.

It is designed to demonstrate a common business automation pattern: taking recurring manual review work and turning it into a repeatable, documented workflow.

---

## Business Problem

Many operations teams rely on recurring alarm reports, spreadsheets, emails, dashboards, or system exports to identify issues that require attention.

The manual process often looks like this:

1. Open a current system alarm report.
2. Compare it against a known issue or reference list.
3. Remove items that are already accounted for.
4. Identify unresolved exceptions.
5. Create a clean report for follow-up.

This process is time-consuming, repetitive, and easy to perform inconsistently.

---

## Solution

This tool automates that workflow by:

- Loading current system status data.
- Loading known discrepancy/reference data.
- Comparing records based on defined business rules.
- Removing accounted-for conditions.
- Adding asset criticality or other useful context.
- Generating a clean output report.

The goal is to reduce manual filtering so reviewers can focus on the items that actually need attention.

---

## Features

- Reads multiple CSV input files.
- Validates required columns before processing.
- Compares current conditions against known discrepancies.
- Filters for active abnormal conditions.
- Adds criticality context from a reference list.
- Generates a clean CSV exception report.
- Optionally generates an Excel report highlighting stale known discrepancies.
- Provides command-line arguments for repeatable use.

---

## Tech Stack

- Python
- pandas
- argparse
- pathlib
- openpyxl

---

## Project Structure

```text
project-name/
│
├── src/
│   ├── app.py
│   ├── models.py
│   └── refine_tools.py
│
├── data/
│   ├── sample_input/
│   └── sample_output/
│
├── docs/
│   └── screenshots/
│
├── README.md
├── requirements.txt
└── .gitignore
```

## Sample Input Files

This demo uses three sample CSV files:

1. Current System Status Report

Represents current asset conditions.

Example columns:

```text 
asset_id, asset_name, current_status, reported_condition, last_updated
```
2. Known Discrepancy List

Represents conditions that have already been reviewed or accounted for.

Example columns:
```text
asset_id, known_condition, owner, date_logged, review_by
```
3. Critical Asset List

Represents asset metadata used to add operational context.

Example columns:

```text
asset_id, asset_name, criticality, system_group
```
## Output

The tool generates a CSV report showing outstanding alarms or discrepancies requiring review.

Example output columns:

```text
asset_id, asset_name, current_status, reported_condition, criticality
```

Optional output:

stale_known_discrepancies.xlsx

This Excel file highlights known discrepancies that are past their review date.

How to Run
1. Clone the repository
```text
git clone https://github.com/your-username/project-name.git
cd project-name
```

2. Create and activate a virtual environment
```text
python -m venv venv
```

On Windows:
```text
venv\Scripts\activate
```
On macOS/Linux:
```text

source venv/bin/activate
```


3. Install dependencies
```text
pip install -r requirements.txt
```
4. Run the report
```text
python src/app.py \
  --status data/sample_input/current_system_status_report.csv \
  --known data/sample_input/known_discrepancy_list.csv \
  --critical data/sample_input/critical_asset_list.csv \
  --output data/sample_output/discrepancy_report.csv
  ```
5. Run with optional stale discrepancy export
```text
python src/app.py \
  --status data/sample_input/current_system_status_report.csv \
  --known data/sample_input/known_discrepancy_list.csv \
  --critical data/sample_input/critical_asset_list.csv \
  --output data/sample_output/discrepancy_report.csv \
  --generate-highlighted \
  --highlight data/sample_output/stale_known_discrepancies.xlsx
```