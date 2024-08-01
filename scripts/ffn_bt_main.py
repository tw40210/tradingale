import bt
import numpy as np
import pandas as pd
from yahoo_fin import stock_info as si

tickers = {
    "sp500": "IVV",
    "cash": "SHY",
    "sectors": ["IYC", "IDU", "IYZ", "IYW", "IYJ", "IYH", "IYF", "IYE", "IYK", "IYM", "IYR"],
}
# Download Data

symbols = tickers["sectors"] + [tickers["sp500"], tickers["cash"]]
data = {k: si.get_data(k) for k in symbols}
prices = pd.DataFrame.from_dict({k: v.adjclose for k, v in data.items()}).dropna()


class StatDrawdown(bt.Algo):
    def __init__(self, lookback=None, lag=None):
        super().__init__()
        self.lookback = lookback if lookback else pd.DateOffset(months=3)
        self.lag = lag if lag else pd.DateOffset(days=0)

    def __call__(self, target):
        selected = target.temp["selected"]
        t0 = target.now - self.lag
        prc = target.universe.loc[(t0 - self.lookback) : t0, selected]
        target.temp["stat"] = prc.to_drawdown_series().iloc[-1]
        return True


class StatInfoRatio(bt.Algo):
    def __init__(self, benchmark, lookback=None, lag=None):
        super().__init__()
        self.benchmark = benchmark

        self.lookback = lookback if lookback else pd.DateOffset(months=3)
        self.lag = lag if lag else pd.DateOffset(days=0)

    def __call__(self, target):
        selected = target.temp["selected"]
        t0 = target.now - self.lag
        prc = target.universe.loc[(t0 - self.lookback) : t0, selected].pct_change().dropna()
        bmk = target.universe.loc[(t0 - self.lookback) : t0, self.benchmark].pct_change().dropna()
        target.temp["stat"] = pd.Series({p: prc[p].calc_information_ratio(bmk) for p in prc})
        return True


sp500 = bt.Strategy(
    "SP500",
    algos=[
        bt.algos.RunQuarterly(),
        bt.algos.SelectAll(),
        bt.algos.SelectThese([tickers["sp500"]]),
        bt.algos.WeighEqually(),
        bt.algos.Rebalance(),
    ],
)


sphmv = bt.Strategy(
    "SPHMV",
    algos=[
        bt.algos.RunQuarterly(),
        bt.algos.SelectAll(),
        bt.algos.SelectThese(tickers["sectors"]),
        StatDrawdown(lookback=pd.DateOffset(years=10)),
        bt.algos.SelectN(5, sort_descending=False),
        StatInfoRatio(
            benchmark=tickers["sp500"],
            lookback=pd.DateOffset(months=7),
            lag=pd.DateOffset(months=1),
        ),
        bt.algos.SelectN(3, sort_descending=True),
        bt.algos.WeighEqually(),
        bt.algos.Rebalance(),
    ],
)

backtest_sp500 = bt.Backtest(sp500, prices)
backtest_sphmv = bt.Backtest(sphmv, prices)
report = bt.run(backtest_sp500, backtest_sphmv)
report.backtests["SPHMV"].security_weights.plot.area()

target_vol = 20
real_vol = prices[tickers["sp500"]].pct_change().rolling(20).std().multiply(np.sqrt(252) * 100)
w = real_vol.map(lambda x: min(1, target_vol / x))
target_weight = pd.DataFrame({"SPHMV": w, "SHY": 1 - w})


# fetch some data
data = bt.get("spy,agg", start="2022-01-01")
print(data.head())
s = bt.Strategy(
    "s1",
    [bt.algos.RunMonthly(), bt.algos.SelectAll(), bt.algos.WeighEqually(), bt.algos.Rebalance()],
)

# create a backtest and run it
test = bt.Backtest(s, data)
res = bt.run(test)

# first let's see an equity curve
res.plot()

# ok and what about some stats?
res.display()

# ok and how does the return distribution look like?
res.plot_histogram()
print("OK")
