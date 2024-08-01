import math

import bt
import src.py_libs.data_process.sql_backtest_base as backtest_db
from src.py_libs.controllers.data_controller import DataController
from src.py_libs.controllers.strategy_controller import StrategyController
from src.py_libs.objects.backtest_types import BacktestInfo
from src.py_libs.utils.tickers import sp500_tickers

tickers = {
    "A_G": ["AAPL", "GOOG"],
    "cash": ["SHY"],
    "sp500": sp500_tickers[:5],
    "my_select": ["MSFT", "AMZN", "NVDA", "META", "HSBC", "LLY", "TSLA"],
    "sp500_index": ["SPY"],
}
symbols = (
    tickers["my_select"]
    + tickers["cash"]
    + tickers["A_G"]
    + tickers["sp500"]
    + tickers["sp500_index"]
)


class BacktestController:
    def __init__(
        self, strategy_controller: StrategyController, data_controller: DataController
    ) -> None:

        self.strategy_controller = strategy_controller
        self.data_controller = data_controller
        self.all_securityList = list(self.data_controller.prices_dict.keys())

        init_backtest_name = "backtest-0"
        init_strategy_name = self.strategy_controller.strategy_order[0]
        self.backtests: dict[str, BacktestInfo] = {}
        self.backtest_order = []

        self._insert_backtests(
            name=init_backtest_name,
            strategy_id=init_strategy_name,
            security_list=self.all_securityList,  # always use full data so far
        )

    def _init_properties(self):
        self.backtests = {}
        self.backtest_order = []

    def update_backtests(self, backtest_info_dict: dict) -> None:
        self._init_properties()

        backtests = backtest_info_dict["backtestInfo"]
        backtest_order = backtest_info_dict["backtestOrder"]
        for backtest_id in backtest_order:
            backtest_info = backtests[backtest_id]
            self._insert_backtests(
                name=backtest_info["id"],
                strategy_id=backtest_info["strategyId"],
                security_list=self.all_securityList,  # always use full data so far
                **backtest_info["additional"]
            )

    def _insert_backtests(
        self, name: str, strategy_id: str, security_list: list[str], **kwargs
    ) -> None:
        strategy = self.strategy_controller.strategies[strategy_id].to_bt_strategy()

        self.backtests[name] = BacktestInfo(
            name=name,
            strategy=strategy,
            strategy_id=strategy_id,
            security_list=security_list,
            **kwargs
        )
        if name not in self.backtest_order:
            self.backtest_order.append(name)

    def run_backtests(self) -> dict:
        data_source = self.data_controller.prices_dataframes
        report = bt.run(
            *[backtest.to_bt_backtest(data_source) for key, backtest in self.backtests.items()]
        )
        report.display()

        return self._get_report_dict(report)

    def fetch_backtests(self) -> dict:
        backtests = {"backtestInfo": {}, "backtestOrder": []}
        for backtest_id in self.backtest_order:
            backtest_dict = {
                "id": self.backtests[backtest_id].name,
                "strategyId": self.backtests[backtest_id].strategy_id,
                "securities": [],
                "additional": self.backtests[backtest_id].additional,
            }
            backtests["backtestOrder"].append(backtest_id)
            backtests["backtestInfo"][backtest_id] = backtest_dict

        return backtests

    def _get_report_dict(self, report: bt.backtest.Result) -> dict[str, dict[str, dict]]:
        report_dict = {}
        prices = report.prices.to_dict()
        stats = report.stats.to_dict()
        for backtest_name in report.backtests.keys():
            backtest_dict = {}
            backtest_dict["prices"] = {str(k): v for k, v in prices[backtest_name].items()}
            backtest_dict["stats"] = {}

            for key, value in stats[backtest_name].items():
                if isinstance(value, (float, int)) and not math.isnan(value):
                    backtest_dict["stats"][key] = value
                else:
                    backtest_dict["stats"][key] = str(value)

            report_dict[backtest_name] = backtest_dict

        return report_dict

    def save_to_db(self):
        session = backtest_db.init_session()
        backtest_db.clear_all_data(session)
        for _, backtest in self.backtests.items():
            backtest_db.insert_backtest(session, backtest)

        backtest_db.insert_backtest_order(session, self.backtest_order)

    def load_from_db(self):
        session = backtest_db.init_session()
        loaded_data = backtest_db.get_all_data(session)

        for _, backtest_info in loaded_data["backtests"].items():
            self._insert_backtests(
                name=backtest_info["id"],
                strategy_id=backtest_info["strategyId"],
                security_list=self.all_securityList,  # always use full data so far
                **backtest_info["additional"]
            )

        self.backtest_order = loaded_data["backtest_order"]
