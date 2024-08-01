import datetime
from abc import ABC, abstractmethod

import pandas as pd
from src.py_libs.objects.enum import AssetType
from src.py_libs.objects.stock_types import MarketQuote


class BasicDataRetriever(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_data(
        self,
        symbols: list,
        start: datetime.datetime,
        end: datetime.datetime,
        interval: datetime.timedelta,
        asset_type: AssetType,
    ) -> dict[str, pd.DataFrame]:
        pass

    @abstractmethod
    def get_latest_quote(self, symbols: list[str]) -> dict[str, MarketQuote]:
        pass
