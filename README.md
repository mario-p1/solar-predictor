# Solar Radiation Predictor

Time series analysis and forecasting of solar radiation, based on satellite data.
Models are trained on SageMaker, tracked in MLflow and deployed to a serverless endpoint.

## ML workflow
1. **Fetch**: the Lambda saves raw radiation data to S3
2. **Preprocess**: a SageMaker Processing job builds features from the raw data and saves them to S3
3. **Train**: a SageMaker Training job trains the model and logs it to MLflow
4. **Register**: the chosen model is registered manually in the MLflow UI
5. **Deploy**: the registered model is deployed to a SageMaker serverless endpoint
6. **Predict**: the endpoint returns predictions

## AWS architecture
- **CloudFormation**: main stack and a separate endpoint stack
- **S3**: raw data, features, training outputs and MLflow artifacts
- **Lambda**: fetches SARAH-3 radiation data from Open-Meteo into S3
- **ECR**: shared Docker image for preprocessing, training and serving
- **SageMaker Processing**: builds the features
- **SageMaker Training**: trains XGBoost on spot instances
- **SageMaker MLflow**: experiment tracking and model registry
- **SageMaker Serverless Endpoint**: serves a registered MLflow model
- **SageMaker Domain**: Studio domain and user profile
- **IAM**: Lambda and SageMaker execution roles

## Setup from scratch
### Requirements
- `uv`
- `make`
- `zip`
- Docker
- AWS CLI (configure with `aws login`)

### Setup
The steps below use the coordinates of Skopje (`42.00`, `21.43`) as an example.

1. Install dependencies and create `.env`
    ```bash
    uv sync
    cp .env.template .env
    ```
2. Create the code bucket and put its name in `CODE_BUCKET`.
3. Find your VPC and subnets, and fill in `VPC_ID` and `SUBNET_IDS` (comma-separated).
4. Upload the Lambda and deploy the main stack
    ```bash
    make upload_lambda
    make deploy_cloudformation
    ```
5. Copy the outputs to `.env`. `MLFLOW_TRACKING_URI` is the `MLFLOW_APP_ARN` value.
    ```bash
    make describe_stacks
    ```
6. Push the Docker image
    ```bash
    make push_image
    ```
7. Fetch the data
    ```bash
    set -a; source .env; set +a
    aws lambda invoke \
        --function-name $FETCH_DATA_FUNCTION_NAME \
        --cli-binary-format raw-in-base64-out \
        --payload '{"lat": "42.00", "long": "21.43"}' \
        /dev/stdout
    ```
8. Run preprocessing and wait for it to finish
    ```bash
    uv run \
        --env-file .env \
        python -m scripts.start_preprocessing \
            --lat 42.00 \
            --long 21.43
    ```
9. Train the model
    ```bash
    uv run \
        --env-file .env \
        python -m scripts.run_train \
            --lat 42.00 \
            --long 21.43
    ```
10. Register the model in the MLflow UI as `SARAH3-predictor`
11. Deploy the model
    ```bash
    uv run \
        --env-file .env \
        python -m scripts.deploy_model \
            SARAH3-predictor/1
    ```
12. Try the endpoint (get the name from `make describe_stacks`)
    ```bash
    uv run \
        --env-file .env \
        python -m scripts.invoke_endpoint \
            <endpoint-name>
    ```

## Notes
Used for saving debug commands.

```bash
# Invoke local model endpoint with sample payload
curl http://127.0.0.1:8080\/invocations -H "Content-Type:application/json" --data-binary "@sample_payload.json"
```