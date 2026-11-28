import json
from datetime import timedelta
from typing import Any

import boto3

from heliocast import openmeteo
from heliocast.features import build_tree_features
from heliocast.utils import LOCATIONS, config, get_current_utc_date


def lambda_handler(event: dict, context: Any):
    # Skopje is the only city with available model, use that for inference
    lat = LOCATIONS["SKOPJE"]["LAT"]
    long = LOCATIONS["SKOPJE"]["LONG"]

    inference_date = get_current_utc_date()
    fetch_previous_days = 10

    raw_df = openmeteo.fetch_sarah3_radiation(
        latitude=lat,
        longitude=long,
        start_date=(inference_date - timedelta(days=fetch_previous_days)).strftime(
            "%Y-%m-%d"
        ),
        end_date=inference_date.strftime("%Y-%m-%d"),
    ).set_index("datetime")

    features_df = build_tree_features(raw_df)

    # Get only current day
    features_df = features_df.loc[lambda x: x.index.date >= inference_date.date()]

    # Filter columns
    features_df = features_df[
        [
            "hour",
            "day_of_year",
            "lag_49",
            "lag_72",
            "lag_168",
            "hour_mean_7d",
        ]
    ].copy()

    # Drop na
    features_df = features_df.dropna()

    raw_df.to_csv("raw_data.csv", index=True)
    features_df.to_csv("features.csv", index=True)

    # Call endpoint
    endpoint_response = boto3.client("sagemaker-runtime").invoke_endpoint(
        EndpointName=config.SARAH3_PREDICTOR_ENDPOINT_NAME,
        ContentType="text/csv",
        Body=features_df.to_csv(index=False),
    )

    inference_results = json.loads(endpoint_response["Body"].read().decode())

    results_df = features_df.assign(prediction=inference_results["predictions"])

    # Sanity check: if prediction is negative, set it to 0
    results_df.loc[lambda x: x["prediction"] < 0, "prediction"] = 0

    results_df.to_csv("results.csv", index=True)

    return {"statusCode": 200, "result": "ok"}
