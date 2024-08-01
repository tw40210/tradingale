from datetime import timedelta

from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from src.py_libs.objects.enum import AssetType


def get_historical_data_file_name(
    st_time_str: str, ed_time_str: str, symbol_name: str, interval: timedelta, asset_type: AssetType
) -> str:
    # Deal symbols with "/"
    symbol_name = symbol_name.replace("/", "-")
    interval_min = int(interval.total_seconds() // 60)

    file_path = f"{st_time_str}_{ed_time_str}_{interval_min}m_{symbol_name}_{asset_type.value}.csv"
    return file_path


def get_symbols_from_file_name(symbol_name: str) -> str:
    # Revert symbols with "/"
    symbol_name = symbol_name.replace("-", "/")
    return symbol_name


def get_alpaca_timestep(interval: timedelta):
    num_mins = int(interval.total_seconds() // 60)

    if num_mins >= 60 * 24:
        num_days = int(num_mins // (60 * 24))
        result = TimeFrame(amount=num_days, unit=TimeFrameUnit.Day)
    elif num_mins >= 60:
        num_hours = int(num_mins // 60)
        result = TimeFrame(amount=num_hours, unit=TimeFrameUnit.Hour)
    else:
        result = TimeFrame(amount=num_mins, unit=TimeFrameUnit.Minute)
    return result
