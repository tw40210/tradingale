from dataclasses import dataclass, field

import bt


@dataclass
class StrategyInfo:
    name: str
    stack_id: str
    algo_stack: list[bt.Algo] = field(default_factory=list)
    algo_ids: list[str] = field(default_factory=list)
    securities: list[str] = field(default_factory=list)
    additional: dict = field(default_factory=dict)

    def to_bt_strategy(self):
        return bt.Strategy(
            name=self.name, algos=self.algo_stack, children=self.securities, **self.additional
        )
