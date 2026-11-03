import pandas as pd

from solar_predictor.storage import find_files_at_loc, read_csv


def read_sarah3(
    location_prefix: str | None, csvs: list[str] | None = None
) -> pd.DataFrame:
    """
    Arguments:
    location_prefix: str | None
        The prefix of the location where the CSV files are stored.
        It is required when `csvs` is None, and ignored otherwise.
    csvs: list[str] | None
        A list of CSV file paths to read. If None, the function read all CSV.
    """
    if csvs is None:
        csvs = find_files_at_loc(location_prefix, "/sarah3.csv")

    dfs = [read_csv(csv) for csv in csvs]
    df = pd.concat(dfs, ignore_index=True)

    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    return df.set_index("datetime")


def drop_incomplete_tail(df: pd.DataFrame) -> pd.DataFrame:
    last_complete_row = df[df.notna().all(axis=1)].iloc[-1]
    return df.loc[df["timestamp"] <= last_complete_row["timestamp"]]


def interpolate_with_lag(series: pd.Series, lag: int) -> pd.Series:
    series = series.copy()

    lagged = series.shift(lag)

    while True:
        filled = series.fillna(lagged)
        if filled.isna().sum() == series.isna().sum():
            break
        series = filled

    return filled
