import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

import pandas as pd
from alpaca.common.rest import RESTClient
from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import (
    BaseBarsRequest,
    CryptoBarsRequest,
    StockBarsRequest,
    StockLatestQuoteRequest,
)
from src import REPO
from src.private_keys.keys import KEY_ID, SERET_KEY
from src.py_libs.objects.basic_data_retriever import BasicDataRetriever
from src.py_libs.objects.enum import AssetType
from src.py_libs.objects.stock_types import MarketQuote
from src.py_libs.utils.data_process import get_alpaca_timestep


@dataclass
class ClientComponents:
    client: RESTClient
    get_bars: Callable
    request_type: BaseBarsRequest


class AlpacaDataLoader(BasicDataRetriever):
    def __init__(self):
        self.stock_client = StockHistoricalDataClient(KEY_ID, SERET_KEY)
        self.crypto_client = CryptoHistoricalDataClient(KEY_ID, SERET_KEY)
        self.saving_folder_path = REPO / "output/historical_data/"
        self.client_switcher = {
            AssetType.Stock: ClientComponents(
                client=self.stock_client,
                get_bars=self.stock_client.get_stock_bars,
                request_type=StockBarsRequest,
            ),
            AssetType.Crypto: ClientComponents(
                client=self.crypto_client,
                get_bars=self.crypto_client.get_crypto_bars,
                request_type=CryptoBarsRequest,
            ),
        }
        self._logger = logging.getLogger(self.__module__)

    def get_data(
        self,
        symbols: list,
        start: datetime,
        end: datetime,
        interval: timedelta,
        asset_type: AssetType,
    ) -> dict[str, pd.DataFrame]:
        """Get data of symbols one by one separately within given period.

        Args:
            symbols: list of symbols to get data
            start: start date
            end: end date
            interval: interval of each data,
            asset_type: Crypto or Stock
            save_file: if save as a csv file

        Returns:
            a dict containing dataframe of symbols
        """

        client_component = self.client_switcher[asset_type]
        request_params = client_component.request_type(
            symbol_or_symbols=symbols,
            timeframe=get_alpaca_timestep(interval),
            start=start,
            end=end,
        )
        data_bars = client_component.get_bars(request_params)

        return data_bars.df

    def get_latest_quote(self, symbols: list[str], asset_type: AssetType) -> dict[str, MarketQuote]:
        def make_market_quote_dict(quote_response: dict) -> dict[str, MarketQuote]:
            market_quote_dict = {}
            for key in quote_response:
                market_quote_dict[key] = MarketQuote(
                    ask_price=quote_response[key].ask_price,
                    ask_size=quote_response[key].ask_size,
                    bid_price=quote_response[key].bid_price,
                    bid_size=quote_response[key].bid_size,
                )
            return market_quote_dict

        client = self.client_switcher[asset_type].client
        if asset_type == AssetType.Stock:
            quote_request = StockLatestQuoteRequest(symbol_or_symbols=symbols)
            latest_quote_response = client.get_stock_latest_quote(quote_request)
            market_quote_dict = make_market_quote_dict(latest_quote_response)
        else:
            raise ValueError(f"Unsupported asset_type: {asset_type}")
        return market_quote_dict
