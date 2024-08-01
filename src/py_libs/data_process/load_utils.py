from pathlib import Path

import pandas as pd
from src import REPO
from src.py_libs.objects.enum import AssetType
from src.py_libs.objects.stock_types import StockMetaData


def load_historical_data(folder_path: Path):
    all_data_raw = {}

    for path in (REPO / folder_path).iterdir():
        symbol_name = str(path.stem).split("_")[-2]
        data = pd.read_csv(path, index_col="Unnamed: 0")
        data.index = pd.to_datetime(data.index)
        all_data_raw[symbol_name] = data
    return all_data_raw


def get_historical_metadata(folder_path: Path) -> dict[str, StockMetaData]:
    all_metadata = {}

    for path in (REPO / folder_path).iterdir():
        file_name = str(path.stem)
        symbol_name = file_name.split("_")[-2]
        start = file_name.split("_")[0]
        end = file_name.split("_")[1]

        all_metadata[symbol_name] = StockMetaData(
            name=symbol_name, start_date=start, end_date=end, type=AssetType.Stock
        )

    return all_metadata


if __name__ == "__main__":
    meta_data = get_historical_metadata(Path("output/historical_data"))
