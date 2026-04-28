import pandas as pd
from typing import Protocol
from pathlib import Path
from models import DataSource



CURRENT_DATE = pd.Timestamp.today().normalize()

#Definite shape of Tool classes
class Tool(Protocol):
    """Define tool interface"""
    def run(self, data: DataSource) -> pd.DataFrame:
        ...


class AlarmComparisonTool:
    """Tool that compares defined discrepancies to current alarms"""

    def run(self, data: DataSource) -> pd.DataFrame:

        current = data.current_system_status.copy()
        known = data.known_discrepancies.copy()
        critical = data.critical_asset.copy()

        current["asset_id"] = current["asset_id"].astype(str).str.strip()
        known["asset_id"] = known["asset_id"].astype(str).str.strip()
        critical["asset_id"] = critical["asset_id"].astype(str).str.strip()

        current["reported_condition"] = current["reported_condition"].astype(str).str.strip()
        known["known_condition"] = known["known_condition"].astype(str).str.strip()
        known = known.rename(columns={"known_condition": "reported_condition"})

        merged = current.merge(known, on=["asset_id", "reported_condition"], how="left", indicator=True)
        excluded = merged[~(merged["_merge"] == "both")]
        excluded = excluded.drop(columns=["_merge"])
        excluded = excluded.dropna(axis="columns", how="all")
        excluded["asset_id"] = excluded["asset_id"].str.strip()

        return excluded



class OutstandingAlarmsTool:
    """Tool that removes any alarms that are no longer active from current alarms"""
    def run(self, current_sys_status: pd.DataFrame, critical_asset: pd.DataFrame) -> pd.DataFrame:

        current_sys_status = current_sys_status.copy()
        critical_asset = critical_asset.copy()

        current_sys_status["asset_id"] = current_sys_status["asset_id"].astype(str).str.strip()
        critical_asset["asset_id"] = critical_asset["asset_id"].astype(str).str.strip()

        in_alarm_state = current_sys_status[(current_sys_status["reported_condition"] != "Normal") &
                                        (current_sys_status["current_status"] == "Available")].copy()
        in_alarm_state = in_alarm_state.merge(critical_asset[["asset_id", "criticality"]], on="asset_id", how="left")
        in_alarm_state["criticality"] = in_alarm_state["criticality"].fillna("none assigned")
        return in_alarm_state



class Highlighter:
    """Highlight known discrepancies that are past their review date."""
    def run(self, row: pd.Series) -> list[str]:
        delta = (CURRENT_DATE - pd.to_datetime(row["review_by"])).days

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

    def generate_report(self, path: Path) -> pd.DataFrame:
        """Generate a clean report of active alarms in a .csv"""
        path.parent.mkdir(parents=True, exist_ok=True)
        unaccounted_alarms = AlarmComparisonTool().run(self.data)
        refined_alarms = OutstandingAlarmsTool().run(unaccounted_alarms, self.data.critical_asset)
        refined_alarms.to_csv(path, index=False)
        return refined_alarms

    def generate_highlighted_discrepancies(self, path: Path) -> None:
        """Generate an Excel report highlighting known discrepancies past their review date."""
        path.parent.mkdir(parents=True, exist_ok=True)
        highlighted_report = self.data.known_discrepancies.style.apply(Highlighter().run, axis=1)
        highlighted_report.to_excel(
            path, index=False)








