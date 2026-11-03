import numpy as np
import pandas as pd


def wma(s: pd.Series, window: int) -> pd.Series:
    weights = np.arange(1, window + 1)
    return s.rolling(window).apply(lambda x: x.dot(weights) / weights.sum(), raw=True)
