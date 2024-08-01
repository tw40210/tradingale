import logging
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from src import REPO
from src.py_libs.objects.basic_data_retriever import BasicDataRetriever
from src.py_libs.objects.enum import AssetType
from src.py_libs.utils.data_process import (
    get_historical_data_file_name,
    get_symbols_from_file_name,
)
from tqdm import tqdm


class LocalDataManager:
    def __init__(self, data_retriever: BasicDataRetriever):
        self.data_retriever = data_retriever
        self._logger = logging.getLogger(self.__module__)
        self.saving_folder_path = REPO / "output/historical_data/"

    def init_data_files(
        self,
        symbols: list,
        start: datetime,
        end: datetime,
        interval: timedelta,
        asset_type: AssetType,
    ):
        symbols_dict = {}
        self._logger.info("Getting Data in fixed period!")
        for symbol in tqdm(symbols):
            symbol_data = self.data_retriever.get_data(
                symbols=[symbol], start=start, end=end, interval=interval, asset_type=asset_type
            )
            symbols_dict[symbol] = symbol_data

            st_time_str = start.strftime("%Y%m%d")
            ed_time_str = end.strftime("%Y%m%d")

            self.saving_folder_path.mkdir(parents=True, exist_ok=True)

            saving_file_path = self.saving_folder_path / get_historical_data_file_name(
                st_time_str, ed_time_str, symbol, interval, asset_type
            )

            symbol_data.to_csv(saving_file_path)

        return symbols_dict

    def update_historical_data(self, csv_file: Path, asset_type: AssetType) -> pd.DataFrame:
        data_delay_hours = 12 if asset_type == AssetType.Stock else 0
        data_pd = pd.read_csv(csv_file, index_col="Unnamed: 0")
        data_pd.index = pd.to_datetime(data_pd.index)

        start, end, interval_str, symbol, file_asset_type = csv_file.stem.split("_")
        interval = timedelta(minutes=int(interval_str[:-1]))
        # change to from end to yesterday, no permission for free account
        new_start = datetime.strptime(end, "%Y%m%d") + timedelta(days=1)
        new_end = datetime.today() - timedelta(hours=data_delay_hours)

        if new_end <= new_start:
            self._logger.info(
                "Updating date is earlier than existing data!" " Return non-updated data."
            )
            return data_pd

        symbol = get_symbols_from_file_name(symbol)
        try:
            symbol_data = self.data_retriever.get_data(
                symbols=[symbol],
                start=new_start,
                end=new_end,
                interval=interval,
                asset_type=asset_type,
            )
        except Exception as e:
            symbol_data = None
            print(f"Fetch data and hit some problems. Set data_bars as None: {e}")

        if symbol_data is None or len(symbol_data) == 0:
            new_symbol_data_pd = data_pd
        else:
            new_symbol_data_pd = pd.concat([data_pd, symbol_data])

        st_time_str = start
        ed_time_str = new_end.strftime("%Y%m%d")
        file_name = get_historical_data_file_name(
            st_time_str, ed_time_str, symbol, interval, asset_type
        )
        new_csv_file = csv_file.parent / file_name
        new_symbol_data_pd.to_csv(new_csv_file)
        if new_csv_file != csv_file:
            csv_file.unlink()

        return new_symbol_data_pd

    def update_all_in_data_dir(self, asset_type: AssetType):
        self._logger.info("Updating existing data to latest date!")
        for file_path in tqdm(self.saving_folder_path.iterdir()):
            start, end, interval_str, symbols, file_asset_type = file_path.stem.split("_")
            self.update_historical_data(file_path, AssetType(file_asset_type))
