-include .env
export

SRC := $(shell find solar_predictor -name '*.py')
.DELETE_ON_ERROR:

STACK_NAME := radiation-forecaster

.PHONY: all
all: build/lambda.zip

build/lambda_base.zip: uv.lock
	rm -rf build/lambda_base build/lambda_base.zip
	mkdir -p build
	uv export \
		--frozen \
		--no-default-groups \
		--no-emit-project \
		-o build/requirements.txt
	uv pip install \
		--no-installer-metadata \
		--no-compile-bytecode \
		--python-platform x86_64-manylinux_2_34 \
		--python 3.14 \
		--target build/lambda_base \
		--only-binary :all: \
		-r build/requirements.txt
	cd build/lambda_base && zip -qr ../lambda_base.zip .

build/lambda.zip: build/lambda_base.zip $(SRC)
	cp build/lambda_base.zip build/lambda.zip
	zip -qr build/lambda.zip solar_predictor -x '*__pycache__*'

.PHONY: clean
clean:
	rm -rf build

.PHONY: format
format:
	uv run ruff check --fix .
	uv run ruff format .

.PHONY: upload_lambda
upload_lambda: build/lambda.zip
	aws s3 cp \
		build/lambda.zip \
		s3://$(CODE_BUCKET)/fetch_data_function.zip
	
.PHONY: deploy
deploy_lambda: upload_lambda
	aws lambda update-function-code \
		--function-name $(FETCH_DATA_FUNCTION_NAME) \
		--s3-bucket $(CODE_BUCKET) \
		--s3-key fetch_data_function.zip

.PHONY: deploy_cloudformation
deploy_cloudformation:
	aws cloudformation deploy \
		--template-file cloudformation.yaml \
		--stack-name $(STACK_NAME) \
		--capabilities CAPABILITY_IAM \
		--parameter-overrides \
			CodeBucket=${CODE_BUCKET} \
			VpcId=${VPC_ID} \
			SubnetIds=${SUBNET_IDS}
	aws cloudformation list-stack-resources \
		--stack-name $(STACK_NAME) \
		--query 'StackResourceSummaries[].[LogicalResourceId,PhysicalResourceId]' \
		--output table
