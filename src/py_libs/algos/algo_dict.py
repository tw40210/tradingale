import bt.algos as bt_algos
import src.py_libs.algos.my_algos as my_algos

ALGO_DICT = {
    "RunOnce": bt_algos.RunOnce,
    "RunDaily": bt_algos.RunDaily,
    "RunWeekly": bt_algos.RunWeekly,
    "RunMonthly": bt_algos.RunMonthly,
    "RunQuarterly": bt_algos.RunQuarterly,
    "RunYearly": bt_algos.RunYearly,
    "SelectAll": bt_algos.SelectAll,
    "SelectRandomly": bt_algos.SelectRandomly,
    "SelectN": bt_algos.SelectN,
    "WeighEqually": bt_algos.WeighEqually,
    "WeighRandomly": bt_algos.WeighRandomly,
    "Not": bt_algos.Not,
    "Or": bt_algos.Or,
    "Rebalance": bt_algos.Rebalance,
    "StatDrawdown": my_algos.StatDrawdown,
    "StatInfoRatio": my_algos.StatInfoRatio,
    "PriceFilterAlgo": my_algos.PriceFilterAlgo,
    "TrendFollowingAlgo": my_algos.TrendFollowingAlgo,
    "MomentumInvestingAlgo": my_algos.MomentumInvestingAlgo,
    "MeanReversionAlgo": my_algos.MeanReversionAlgo,
    "Empty": my_algos.Empty,
}
