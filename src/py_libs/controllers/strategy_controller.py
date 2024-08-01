import src.py_libs.data_process.sql_strategy_base as strategy_db
from src.py_libs.controllers.algo_controller import AlgoStackController
from src.py_libs.objects.strategy_types import StrategyInfo


class StrategyController:
    def __init__(self, algo_stack_controller: AlgoStackController) -> None:
        init_strategy_name = "strategy-0"
        self.strategies: dict[str, StrategyInfo] = {
            init_strategy_name: StrategyInfo(name=init_strategy_name, stack_id="stack-0")
        }
        self.strategy_order: list[str] = [init_strategy_name]
        self.algo_stack_controller = algo_stack_controller

    def _init_properties(self):
        self.strategies: dict[str, StrategyInfo] = {}
        self.strategy_order: list[str] = []

    def update_strategies(self, strategy_info_dict: dict) -> None:
        self._init_properties()
        strategies = strategy_info_dict["strategyInfo"]
        strategy_order = strategy_info_dict["strategyOrder"]
        for strategy_id in strategy_order:
            strategy_info = strategies[strategy_id]
            self._insert_strategy(
                name=strategy_info["id"],
                stack_id=strategy_info["stackId"],
                securities=strategy_info["securities"],
                **strategy_info["additional"]
            )

    def fetch_strategies(self) -> dict:
        strategies = {"strategyInfo": {}, "strategyOrder": []}
        for strategy_id in self.strategy_order:
            strategy_dict = {
                "id": self.strategies[strategy_id].name,
                "stackId": self.strategies[strategy_id].stack_id,
                "securities": self.strategies[strategy_id].securities,
                "additional": self.strategies[strategy_id].additional,
            }
            strategies["strategyOrder"].append(strategy_id)
            strategies["strategyInfo"][strategy_id] = strategy_dict

        return strategies

    def _insert_strategy(self, name: str, stack_id: str, securities: list[str], **kwargs) -> None:
        algo_stack = self.algo_stack_controller.get_algo_object_list(stack_id)
        algo_ids = self.algo_stack_controller.get_algo_ids(stack_id)
        self.strategies[name] = StrategyInfo(
            name=name,
            stack_id=stack_id,
            algo_stack=algo_stack,
            algo_ids=algo_ids,
            securities=securities,
            additional=kwargs,
        )
        if name not in self.strategy_order:
            self.strategy_order.append(name)

    def save_to_db(self):
        session = strategy_db.init_session()
        strategy_db.clear_all_data(session)
        for _, strategy in self.strategies.items():
            strategy_db.insert_strategy(session, strategy)

        strategy_db.insert_stack_order(session, self.strategy_order)

    def load_from_db(self):
        session = strategy_db.init_session()
        loaded_data = strategy_db.get_all_data(session)

        for _, strategy_info in loaded_data["strategies"].items():
            self._insert_strategy(
                name=strategy_info["id"],
                stack_id=strategy_info["stackId"],
                securities=strategy_info["securities"],
                **strategy_info["additional"]
            )

        self.strategy_order = loaded_data["strategy_order"]
