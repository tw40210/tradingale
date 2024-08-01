from dataclasses import asdict, dataclass, field

init_algo_additional = {
    "bool": {},
    "int": {},
    "float": {},
    "category": {},
}


@dataclass
class AlgoInfo:
    id: str = "0"
    content: str = "Default Algo"
    algoType: str = "Empty"
    additional: dict = field(default_factory=dict)

    def __post_init__(self):
        if len(self.additional) == 0:
            self.additional = init_algo_additional

    def get_formatted_additional(self) -> dict:
        # Props without prop types to be directly sent to Algo object
        all_props = {}

        for prop_name, prop_value in self.additional["bool"].items():
            if prop_value == "True":
                prop_value = True
            elif prop_value == "False":
                prop_value = False
            else:
                raise ValueError(
                    f" Unexpected prop value in algo: "
                    f"AlgoInfo id:{self.id}, bool_prop: {prop_name}-{prop_value}"
                )
            all_props[prop_name] = prop_value

        for prop_name, prop_value in self.additional["int"].items():
            all_props[prop_name] = int(prop_value)

        for prop_name, prop_value in self.additional["float"].items():
            all_props[prop_name] = float(prop_value)

        for prop_name, prop_value in self.additional["category"].items():
            all_props[prop_name] = prop_value

        return all_props


@dataclass
class AlgoStack:
    id: str = "stack-0"
    title: str = "Default stack"
    algoIds: list[str] = None

    def __post_init__(self):
        if self.algoIds is None:
            self.algoIds = ["0"]


@dataclass
class AlgoStackContext:
    algos: dict[str, AlgoInfo] = None
    algo_stack_info: dict[str, AlgoStack] = None
    stack_order: list[str] = None

    def __post_init__(self):
        if self.algos is None:
            self.algos = {"0": AlgoInfo()}
        if self.algo_stack_info is None:
            self.algo_stack_info = {"stack-0": AlgoStack()}
        if self.stack_order is None:
            self.stack_order = ["stack-0"]

    def to_dict(self) -> dict:
        return {
            "algos": {k: asdict(v) for k, v in self.algos.items()},
            "algoStackInfo": {k: asdict(v) for k, v in self.algo_stack_info.items()},
            "stackOrder": self.stack_order,
        }

    def update_from_dict(self, input_dict: dict[str, dict]) -> None:
        tmp_algos = {}

        for algo_id, algo in input_dict["algos"].items():
            tmp_algos[algo_id] = AlgoInfo(**algo)
        self.algos = tmp_algos

        tmp_algoStackInfo = {}

        for stack_id, stack in input_dict["algoStackInfo"].items():
            tmp_algoStackInfo[stack_id] = AlgoStack(**stack)
        self.algo_stack_info = tmp_algoStackInfo

        self.stack_order = input_dict["stackOrder"]
