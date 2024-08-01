import bt
import pandas as pd


class StatDrawdown(bt.Algo):
    def __init__(self, lookback=None, lag=None):
        super().__init__()
        self.lookback = pd.DateOffset(days=lookback) if lookback else pd.DateOffset(months=3)
        self.lag = pd.DateOffset(days=lag) if lag else pd.DateOffset(days=0)

    def __call__(self, target):
        selected = target.temp["selected"]
        t0 = target.now - self.lag
        prc = target.universe.loc[(t0 - self.lookback) : t0, selected]
        target.temp["stat"] = prc.to_drawdown_series().iloc[-1]
        return True


class StatInfoRatio(bt.Algo):
    def __init__(
        self,
        benchmark: str,
        lookback: int | None = None,
        lag: int | None = None,
    ):
        super().__init__()
        self.benchmark = benchmark

        self.lookback = pd.DateOffset(days=lookback) if lookback else pd.DateOffset(months=3)
        self.lag = pd.DateOffset(days=lag) if lag else pd.DateOffset(days=0)

    def __call__(self, target):
        selected = target.temp["selected"]
        t0 = target.now - self.lag
        prc = target.universe.loc[(t0 - self.lookback) : t0, selected].pct_change().dropna()
        bmk = target.universe.loc[(t0 - self.lookback) : t0, self.benchmark].pct_change().dropna()
        target.temp["stat"] = pd.Series({p: prc[p].calc_information_ratio(bmk) for p in prc})
        return True


class PriceFilterAlgo(bt.Algo):
    def __init__(self, lookback: int = None, lag: int = None):
        super().__init__()
        self.lookback = pd.DateOffset(days=lookback) if lookback else pd.DateOffset(months=3)
        self.lag = pd.DateOffset(days=lag) if lag else pd.DateOffset(days=0)

    def init(self, target: bt.core.Strategy):
        # Calculate highest and lowest price in the past window
        selected = target.temp["selected"]
        t0 = target.now - self.lag
        highest_price = target.universe.loc[(t0 - self.lookback) : t0, selected].max().dropna()
        lowest_price = target.universe.loc[(t0 - self.lookback) : t0, selected].min().dropna()
        current_price = target.universe.loc[target.now, selected].dropna()
        price_condition = (current_price - lowest_price) / (highest_price - lowest_price)
        return price_condition

    def __call__(self, target):
        target.temp["stat"] = self.init(target)
        return True


class TrendFollowingAlgo(bt.Algo):
    """
    Buy in when gap value is negative, which means the price is going up.
    """

    # signals["short_ma"] = data["Close"].rolling(window=short_window).mean()
    # signals["long_ma"] = data["Close"].rolling(window=long_window).mean()
    #
    # signals["signal"] = np.where(signals["short_ma"] > signals["long_ma"], 1, 0)
    # signals["signal"] = np.where(signals["short_ma"] < signals["long_ma"], -1, signals["signal"])

    def __init__(
        self,
        short_window: int = 10,
        long_window: int = 30,
        lookback: int | None = None,
        lag: int | None = None,
    ):
        super().__init__()
        self.lookback = pd.DateOffset(days=lookback) if lookback else pd.DateOffset(months=3)
        self.lag = pd.DateOffset(days=lag) if lag else pd.DateOffset(days=0)
        self.short_window = pd.DateOffset(days=short_window)
        self.long_window = pd.DateOffset(days=long_window)

    def init(self, target: bt.core.Strategy):
        # Calculate highest and lowest price in the past window
        t0 = target.now - self.lag
        short_mean = target.universe.loc[(t0 - self.short_window) : t0].mean().dropna()
        long_mean = target.universe.loc[(t0 - self.long_window) : t0].mean().dropna()
        long_std = target.universe.loc[(t0 - self.long_window) : t0].std().dropna()

        short_mean = short_mean / (long_std + 1e-5)
        long_mean = long_mean / (long_std + 1e-5)

        gap = long_mean - short_mean

        return gap

    def __call__(self, target):
        target.temp["stat"] = self.init(target)
        return True


class MomentumInvestingAlgo(bt.Algo):
    """
    Buy in when pct_change value is positive.
    """

    # roc = data["Close"].pct_change(window)
    #
    # signals["signal"] = np.where(roc > 0, 1, 0)
    # signals["signal"] = np.where(roc < 0, -1, signals["signal"])

    def __init__(
        self,
        window: int = 5,
        num_std: int = 1,
        lookback: int | None = None,
        lag: int | None = None,
    ):
        super().__init__()
        self.window_days = pd.DateOffset(days=window)
        self.lookback = pd.DateOffset(days=lookback) if lookback else pd.DateOffset(months=3)
        self.lag = pd.DateOffset(days=lag) if lag else pd.DateOffset(days=0)

    def init(self, target: bt.core.Strategy):
        # Calculate highest and lowest price in the past window
        t0 = target.now - self.lag
        rows_len = target.universe.loc[(t0 - self.window_days) : t0].shape[0]
        pct_change = (
            target.universe.loc[(t0 - self.window_days) : t0]
            .pct_change(rows_len - 1)
            .tail(1)
            .dropna()
        )

        # Squeeze DataFrame to Series if there is data. Use 0 otherwise.
        if pct_change.shape[0] == 1:
            pct_change = pct_change.squeeze()
        else:
            pct_change = pd.Series([0] * pct_change.shape[1], index=pct_change.columns)

        return pct_change

    def __call__(self, target):
        target.temp["stat"] = self.init(target)
        return True


class MeanReversionAlgo(bt.Algo):
    # ma = data["Close"].rolling(window=window).mean()
    # std = data["Close"].rolling(window=window).std()
    #
    # signals["signal"] = np.where(data["Close"] < (ma - num_std * std), 1, 0)
    # signals["signal"] = np.where(data["Close"] > (ma + num_std * std), -1, signals["signal"])

    def __init__(
        self,
        window: int = 5,
        num_std: int = 1,
        lookback: int | None = None,
        lag: int | None = None,
    ):
        super().__init__()
        self.lookback = pd.DateOffset(days=lookback) if lookback else pd.DateOffset(months=3)
        self.lag = pd.DateOffset(days=lag) if lag else pd.DateOffset(days=0)

    def init(self, target: bt.core.Strategy):
        # Calculate highest and lowest price in the past window
        t0 = target.now - self.lag
        target.universe.loc[(t0 - self.lookback) : t0].max().dropna()
        highest_price = target.universe.loc[(t0 - self.lookback) : t0].max().dropna()
        lowest_price = target.universe.loc[(t0 - self.lookback) : t0].min().dropna()
        current_price = target.universe.loc[target.now].dropna()
        price_condition = (current_price - lowest_price) / (highest_price - lowest_price)
        return price_condition

    def __call__(self, target):
        target.temp["stat"] = self.init(target)
        return True


class Empty(bt.Algo):
    def __init__(self):
        super().__init__()

    def __call__(self, _):
        return True
