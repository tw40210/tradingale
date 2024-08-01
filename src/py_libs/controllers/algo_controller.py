import bt
import src.py_libs.data_process.sql_algo_base as algo_db
from src.py_libs.algos.algo_dict import ALGO_DICT
from src.py_libs.objects.algo_types import AlgoStackContext


class AlgoStackController:
    def __init__(self) -> None:
        self.algo_stacks_context: AlgoStackContext = AlgoStackContext()

    def fetch_algo_stacks(self) -> dict:
        return self.algo_stacks_context.to_dict()

    def update_algo_stacks(self, algo_stacks_dict: dict) -> None:
        self.algo_stacks_context.update_from_dict(algo_stacks_dict)

    def get_algo_object_list(self, stack_id: str) -> list[bt.Algo]:
        algo_object_list = []
        algo_ids = self.algo_stacks_context.algo_stack_info[stack_id].algoIds
        for algo_id in algo_ids:
            algo_type = self.algo_stacks_context.algos[algo_id].algoType
            algo_prop = self.algo_stacks_context.algos[algo_id].get_formatted_additional()
            algo_object_list.append(ALGO_DICT[algo_type](**algo_prop))

        return algo_object_list

    def get_algo_ids(self, stack_id: str) -> list[str]:
        return self.algo_stacks_context.algo_stack_info[stack_id].algoIds

    def load_from_db(self):
        session = algo_db.init_session()
        loaded_data = algo_db.get_all_data(session)
        self.algo_stacks_context = AlgoStackContext(**loaded_data)

    def save_to_db(self):
        session = algo_db.init_session()
        algo_db.clear_all_data(session)
        for _, algo in self.algo_stacks_context.algos.items():
            algo_db.insert_algo(session, algo)

        for _, stack in self.algo_stacks_context.algo_stack_info.items():
            algo_db.insert_stack(session, stack)

        algo_db.insert_stack_order(session, self.algo_stacks_context.stack_order)
