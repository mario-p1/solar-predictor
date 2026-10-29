from typing import Any

import pandas as pd

from solar_predictor import openmeteo, storage

DEFAULT_START_DATE = "2025-01-01"


def resolve_start_date(location_prefix: str) -> str:
    state = storage.read_state(location_prefix)
    if state is None:
        return DEFAULT_START_DATE
    return (pd.Timestamp(state["last_date"]) + pd.Timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )


def lambda_handler(event: dict, context: Any):
    lat = float(event["lat"])
    long = float(event["long"])

    location_prefix = storage.get_location_prefix(lat, long)

    start_date = event.get("start_date") or resolve_start_date(location_prefix)
    end_date = event.get("end_date") or openmeteo.calculate_sarah3_last_available_date()

    if start_date > end_date:
        return {"statusCode": 200, "result": "No new data to fetch."}

    df = openmeteo.fetch_sarah3_radiation(lat, long, start_date, end_date)
    df = openmeteo.transform_sarah3_df(df)

    if df.empty:
        return {"statusCode": 200, "result": "No data returned."}

    affected_files = []
    last_date = None

    for year, df_year in df.groupby(df["datetime"].dt.year):
        year_last_date = openmeteo.last_complete_day(
            df_year, openmeteo.SARAH3_ENTRIES_PER_DAY
        )

        file_key = storage.get_year_sarah3_file_key(location_prefix, year)
        if storage.file_exists(storage.data_bucket, file_key):
            df_year = pd.concat([storage.read_csv(file_key), df_year])
            df_year = df_year.sort_values(by="timestamp")
            df_year = df_year.drop_duplicates("timestamp", keep="last")

        # Save csv and state
        storage.write_csv(file_key, df_year, index=False)
        affected_files.append(file_key)

        if year_last_date is not None:
            last_date = year_last_date
            storage.write_state(location_prefix, last_date)

    return {
        "statusCode": 200,
        "result": {"affected_files": affected_files, "last_date": last_date},
    }
