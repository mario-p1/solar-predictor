import pandas as pd
import requests

BASE_URL = "https://satellite-api.open-meteo.com/v1/archive"
VARIABLES = [
    "shortwave_radiation",
    "direct_radiation",
    "diffuse_radiation",
    "direct_normal_irradiance",
]
SARAH3_ENTRIES_PER_DAY = 24 * 2  # every 30 minutes


def fetch_sarah3_radiation(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    variables: list[str] = VARIABLES,
) -> pd.DataFrame:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(variables),
        "models": "eumetsat_sarah3",
        "timeformat": "unixtime",
        "timezone": "GMT",
        "temporal_resolution": "native",
    }
    print(f"Fetching radiation data from {BASE_URL} with {params}")

    response = requests.get(BASE_URL, params=params, timeout=60)
    response.raise_for_status()

    df = pd.DataFrame(response.json()["hourly"]).rename(columns={"time": "timestamp"})
    df = df.sort_values(by="timestamp")

    return df


def transform_sarah3_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    return df


def last_complete_day(df: pd.DataFrame, entries_per_day: int) -> str | None:
    complete_rows = df.dropna(how="any")
    rows_per_day = complete_rows.groupby(complete_rows["datetime"].dt.date).size()
    complete_days = rows_per_day[rows_per_day == entries_per_day]
    if complete_days.empty:
        return None
    return complete_days.index[-1].strftime("%Y-%m-%d")
