import time

import boto3
import typer

from heliocast import storage
from heliocast.utils import config


def main(
    lat: str = typer.Option(..., help="Latitude"),
    long: str = typer.Option(..., help="Longitude"),
):
    location_prefix = storage.get_raw_data_prefix(lat, long)
    features_prefix = storage.get_features_prefix(lat, long)
    job_name = f"build-tree-features-{int(time.time())}"

    sagemaker = boto3.client("sagemaker")
    sagemaker.create_processing_job(
        ProcessingJobName=job_name,
        RoleArn=config.SAGEMAKER_ROLE_ARN,
        AppSpecification={
            "ImageUri": f"{config.IMAGE_REPO_URI}:latest",
            "ContainerEntrypoint": ["python", "-m", "heliocast.preprocess"],
        },
        Environment={"DATA_BUCKET": config.DATA_BUCKET},
        ProcessingResources={
            "ClusterConfig": {
                "InstanceCount": 1,
                "InstanceType": "ml.t3.medium",
                "VolumeSizeInGB": 5,
            }
        },
        ProcessingInputs=[
            {
                "InputName": "raw",
                "S3Input": {
                    "S3Uri": f"s3://{config.DATA_BUCKET}/{location_prefix}",
                    "LocalPath": "/opt/ml/processing/input",
                    "S3DataType": "S3Prefix",
                    "S3InputMode": "File",
                },
            }
        ],
        ProcessingOutputConfig={
            "Outputs": [
                {
                    "OutputName": "features",
                    "S3Output": {
                        "S3Uri": f"s3://{config.DATA_BUCKET}/{features_prefix}",
                        "LocalPath": "/opt/ml/processing/output",
                        "S3UploadMode": "EndOfJob",
                    },
                }
            ]
        },
        StoppingCondition={"MaxRuntimeInSeconds": 1800},
    )
    print(f"Started {job_name}")


if __name__ == "__main__":
    typer.run(main)
