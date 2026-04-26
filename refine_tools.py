import pandas as pd
from typing import Protocol
from dataclasses import dataclass

#Convert assets
critical_asset_df = pd.read_csv("data/critical_asset_list.csv")
current_sys_status = pd.read_csv("data/current_system_status_report.csv")
known_discrepancy_df = pd.read_csv("data/known_discrepancy_list.csv")

#Define Tools for handling assets

@dataclass
class DataSource:
    critical_asset: pd.DataFrame
    current_system_status: pd.DataFrame
    known_discrepancies: pd.DataFrame


class Tool(Protocol):

    def run(self, data: DataSource) -> pd.DataFrame:
        ...



class AlarmComparisonTool:

    def run(self, data: DataSource) -> None:
        merged = pd.merge(data.current_system_status, data.known_discrepancies, on='asset_id', how='outer', indicator=True)
        excluded = merged[~(merged["_merge"] == "both")]
        excluded.drop("_merge", axis=1, inplace=True)
        excluded.dropna(axis='columns', how='all', inplace=True)
        data.current_sys_status = excluded


class OutstandingAlarmsTool:

    def run(self, data: DataSource) -> pd.DataFrame:
        current_sys_status = data.current_system_status
        in_alarm_state = current_sys_status[(current_sys_status["reported_condition"] != "Normal") &
                                        (current_sys_status["current_status"] == "Available")]
        return in_alarm_state


class Refiner:

    def generate_report(self, data: DataSource) -> None:
        AlarmComparisonTool().run(data)
        refined_alarms = OutstandingAlarmsTool().run(data)
        refined_alarms.to_csv("data/comparison.csv", index=False)


data = DataSource(critical_asset=critical_asset_df,
                  current_system_status=current_sys_status,
                  known_discrepancies=known_discrepancy_df,
                  )








