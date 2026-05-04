from dataclasses import dataclass
import pandas as pd

@dataclass
class DataSource:
    """Define standard names for accessing data"""
    critical_asset: pd.DataFrame
    current_system_status: pd.DataFrame
    known_discrepancies: pd.DataFrame