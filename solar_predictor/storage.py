import json
import os

import boto3
import pandas as pd

s3 = boto3.client("s3")
data_bucket = os.environ["DATA_BUCKET"]


def file_exists(bucket: str, key: str):
    return s3.list_objects_v2(Bucket=bucket, Prefix=key).get("KeyCount", 0) > 0


def get_location_prefix(latitude: float, longitude: float):
    return f"raw/lat={latitude},long={longitude}/"


def get_year_sarah3_file_key(location_prefix: str, year: int):
    return f"{location_prefix}year={year}/sarah3.csv"


def get_state_file_key(prefix: str):
    return f"{prefix}state.json"


def write_state(prefix: str, last_date: str):
    s3.put_object(
        Bucket=data_bucket,
        Key=get_state_file_key(prefix),
        Body=json.dumps({"last_date": last_date}),
    )


def read_state(prefix: str):
    state_file_key = get_state_file_key(prefix)
    if file_exists(data_bucket, state_file_key):
        state_obj = s3.get_object(Bucket=data_bucket, Key=state_file_key)
        state = json.loads(state_obj["Body"].read())
        print(f"Found state file, last date: {state['last_date']}")
        return state
    return None


def write_csv(file_key: str, df: pd.DataFrame, index: bool = True):
    s3.put_object(
        Bucket=data_bucket,
        Key=file_key,
        Body=df.to_csv(index=index),
    )


def read_csv(file_key: str):
    obj = s3.get_object(Bucket=data_bucket, Key=file_key)
    return pd.read_csv(obj["Body"])


def find_files_at_loc(at_location_prefix: str, filename_end: str) -> list[str]:
    paginator = s3.get_paginator("list_objects_v2")
    keys = [
        obj["Key"]
        for page in paginator.paginate(Bucket=data_bucket, Prefix=at_location_prefix)
        for obj in page.get("Contents", [])
        if obj["Key"].endswith(filename_end)
    ]

    return sorted(keys)
