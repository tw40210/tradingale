from dataclasses import dataclass, field

import bt
import pandas as pd


@dataclass
class BacktestInfo:
    name: str
    strategy: bt.Strategy
    strategy_id: str
    security_list: list[str] = field(default_factory=list)
    additional: dict = field(default_factory=dict)

    def to_bt_backtest(self, data_source: pd.DataFrame):
        return bt.Backtest(
            name=self.name, strategy=self.strategy, data=data_source[self.security_list]
        )
