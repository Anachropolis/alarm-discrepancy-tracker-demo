import pandas as pd
from typing import Protocol
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

@dataclass
class DataSource:
    """Define standard names for accessing data"""
    critical_asset: pd.DataFrame
    current_system_status: pd.DataFrame
    known_discrepancies: pd.DataFrame


CURRENT_TIME = datetime.now().strftime('%Y-%m-%d')

#Definite shape of Tool classes
class Tool(Protocol):
    """Define tool interface"""
    def run(self, data: DataSource) -> pd.DataFrame:
        ...


class AlarmComparisonTool:
    """Tool that compares defined discrepancies to current alarms"""
    def run(self, data: DataSource) -> None:
        merged = pd.merge(data.current_system_status, data.known_discrepancies, on='asset_id', how='outer', indicator=True)
        excluded = merged[~(merged["_merge"] == "both")]
        excluded.drop("_merge", axis=1, inplace=True)
        excluded.dropna(axis='columns', how='all', inplace=True)
        excluded['asset_id'] = excluded['asset_id'].str.strip()
        data.critical_asset['asset_id'] = data.critical_asset['asset_id'].str.strip()
        data.current_sys_status = excluded


class OutstandingAlarmsTool:
    """Tool that removes any alarms that are no longer active from current alarms"""
    def run(self, data: DataSource) -> pd.DataFrame:
        current_sys_status = data.current_system_status
        in_alarm_state = current_sys_status[(current_sys_status["reported_condition"] != "Normal") &
                                        (current_sys_status["current_status"] == "Available")]
        in_alarm_state = in_alarm_state.merge(data.critical_asset[['asset_id', 'criticality']], on='asset_id', how='left')
        in_alarm_state["criticality"] = in_alarm_state["criticality"].fillna("none assigned")
        return in_alarm_state


class ReportHighlighter:

    def run(self, row: pd.Series):
        # row["review_by"] = pd.Timestamp(row["review_by"])
        delta = (pd.to_datetime(CURRENT_TIME) - pd.to_datetime(row["review_by"])).days

        if delta > 60:
            style = "background-color: red"
        elif delta > 30:
            style = "background-color: yellow"
        else:
            style = ""

        return [style] * len(row)


class Highlighter:

    def run(self, row: pd.Series) -> list[str]:
        delta = (pd.to_datetime(CURRENT_TIME) - pd.to_datetime(row["review_by"])).days

        if delta > 60:
            style = "background-color: red"
        elif delta > 30:
            style = "background-color: yellow"
        else:
            style = ""

        return [style] * len(row)


class ReportRefiner:
    """Runs Tools and generates a clean report of active alarms in a .csv"""
    def __init__(self, data: DataSource):
        self.data = data

    def generate_report(self, path: Path) -> None:
        AlarmComparisonTool().run(self.data)
        refined_alarms = OutstandingAlarmsTool().run(self.data)
        refined_alarms.to_csv(path, index=False)

    def generate_highlighted_discrepancies(self, path: Path) -> None:
        highlighted_report = self.data.known_discrepancies.style.apply(Highlighter().run, axis=1)
        highlighted_report.to_excel(
            path, index=False)








