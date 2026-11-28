import numpy as np
import pandas as pd


def wma(s: pd.Series, window: int) -> pd.Series:
    weights = np.arange(1, window + 1)
    return s.rolling(window).apply(lambda x: x.dot(weights) / weights.sum(), raw=True)


def resample_to_hourly(df: pd.DataFrame) -> pd.DataFrame:
    return df.resample("h", closed="right", label="right").mean()


def build_tree_features(
    df: pd.DataFrame, target_column: str = "shortwave_radiation"
) -> pd.DataFrame:
    # Resample to hourly
    df = resample_to_hourly(df)

    # Label rows by the start of their hourly window instead of the end
    df.index = df.index - pd.Timedelta(hours=1)

    # Create featurs df
    features_df = pd.DataFrame(index=df.index)

    target = df[target_column]

    features_df["hour"] = df.index.hour
    features_df["day_of_year"] = df.index.day_of_year

    # SARAH-3 lags <= 48h, last safe lag is 49
    features_df["lag_49"] = target.shift(49)
    features_df["lag_72"] = target.shift(72)
    features_df["lag_168"] = target.shift(168)
    features_df["hour_mean_7d"] = (
        target.shift(72).groupby(df.index.hour).transform(lambda x: x.rolling(7).mean())
    )
    features_df["target"] = target

    return features_df
