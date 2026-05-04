import refine_tools
import argparse
from pathlib import Path
import pandas as pd
from models import DataSource


def parse_args():
    """Define and parse command line arguments"""
    parser = argparse.ArgumentParser(description="""1) Generate a list of outstanding alarms by comparing 
                                                        a current system status report, known discrepancy list, 
                                                        and a critical asset list.
                                                    2) Generate a new version of the known discrepancy list that 
                                                    highlights any conditions persisting beyond their 'review by' date.""")

    parser.add_argument("--status", required=True, help="filepath to current_system_status_report.csv")
    parser.add_argument("--known", required=True, help="filepath to known_discrepancy_list")
    parser.add_argument("--critical", required=True, help="filepath to critical_asset_list.csv")
    parser.add_argument("--output", default="./data/discrepancy_report.csv", help="filepath you would like to store refined report in")
    parser.add_argument("--highlight", default="./data/stale_known_discrepancies.xlsx", help="filepath you would like to store highlighted report in")
    parser.add_argument(
        "--generate-highlighted",
        action="store_true",
        help="Generate an Excel file highlighting stale known discrepancies."
    )

    return parser.parse_args()

def validate_columns(df: pd.DataFrame, required_columns: set[str], file_label: str) -> None:
    """Validate the columns present in the dataframe"""
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"{file_label} is missing required columns: {', '.join(sorted(missing))}"
        )


def main():

    args = parse_args()

    status_path = Path(args.status)
    known_path = Path(args.known)
    critical_path = Path(args.critical)
    output_path = Path(args.output)
    highlight_path = Path(args.highlight)
    data = DataSource(critical_asset=pd.read_csv(critical_path),
            current_system_status=pd.read_csv(status_path),
            known_discrepancies=pd.read_csv(known_path))

    validate_columns(
        data.current_system_status,
        {"asset_id", "asset_name", "current_status", "reported_condition"},
        "Current system status report"
    )

    validate_columns(
        data.known_discrepancies,
        {"asset_id", "known_condition", "review_by"},
        "Known discrepancy list"
    )

    validate_columns(
        data.critical_asset,
        {"asset_id", "asset_name", "criticality"},
        "Critical asset list"
    )

    print("Starting operations discrepancy review...")
    print(f"Current system status file: {status_path}")
    print(f"Known discrepancy file: {known_path}")
    print(f"Critical asset file: {critical_path}")
    refine = refine_tools.ReportRefiner(data)
    refined_alarms = refine.generate_report(output_path)
    print(f"Output file: {output_path}")
    if args.generate_highlighted:
        print("Generating stale known discrepancies...")
        refine.generate_highlighted_discrepancies(highlight_path)
        print(f"Output file: {highlight_path}")


    print("\nOperations discrepancy review complete.")
    print(f"Current status records processed: {len(data.current_system_status)}")
    print(f"Known discrepancies loaded: {len(data.known_discrepancies)}")
    print(f"Critical assets loaded: {len(data.critical_asset)}")
    print(f"Outstanding alarms requiring review: {len(refined_alarms)}")
    print(f"Output file: {output_path}")


if __name__ == "__main__":
    main()



