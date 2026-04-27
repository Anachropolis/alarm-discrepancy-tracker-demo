import refine_tools
import argparse
from pathlib import Path
from dataclasses import dataclass
import pandas as pd

@dataclass
class DataSource:
    """Define standard names for accessing data"""
    critical_asset: pd.DataFrame
    current_system_status: pd.DataFrame
    known_discrepancies: pd.DataFrame


def parse_args():
    parser = argparse.ArgumentParser(description="""1) Generate a list of outstanding alarms by comparing 
                                                        a current system status report, known discrepancy list, 
                                                        and a critical asset list.
                                                    2) Generate a new version of the known discrepancy list that 
                                                    highlights any conditions persisting beyond their 'review by' date.""")

    parser.add_argument("--status", required=True, help="filepath to current_system_status_report.csv")
    parser.add_argument("--known", required=True, help="filepath to known_discrepancy_list")
    parser.add_argument("--critical", required=True, help="filepath to critical_asset_list.csv")
    parser.add_argument("--output", default="./data/discrepancy_report.csv", help="filepath you would like to store refined report in")
    parser.add_argument("--highlight", default="./data/highlighted_known_discrepancies.xlsx", help="filepath you would like to store highlighted report in")

    return parser.parse_args()


def main():

    args = parse_args()

    status_path = Path(args.status)
    # if status_path.exists()
    known_path = Path(args.known)
    critical_path = Path(args.critical)
    output_path = args.output
    data = DataSource(critical_asset=pd.read_csv(critical_path),
            current_system_status=pd.read_csv(status_path),
            known_discrepancies=pd.read_csv(known_path))

    refine = refine_tools.ReportRefiner(data)
    refine.generate_report(output_path)


if __name__ == "__main__":
    main()



