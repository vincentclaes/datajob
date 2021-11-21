# Data Pipeline Pyspark

we have a [pyspark job](./glue_job/glue_pyspark_example.py) that:

- reads the dataset `iris_dataset.csv` from s3
- dumps the result back to s3 as a parquet file


## Deploy

    git clone git@github.com:vincentclaes/datajob.git
    cd datajob

    pip install poetry --upgrade
    poetry shell
    poetry install

    cd examples/data_pipeline_pyspark
    export AWS_PROFILE=default
    export AWS_DEFAULT_REGION=eu-west-1
    export AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text --profile $AWS_PROFILE)

    cdk bootstrap aws://$AWS_ACCOUNT/$AWS_DEFAULT_REGION

    python setup.py bdist_wheel
    cdk deploy --app "python datajob_stack.py" --require-approval never

upload the dataset to the data bucket

    aws s3 cp ./dataset/iris_dataset.csv s3://datajob-python-pyspark-my-stage/raw/iris_dataset.csv

## Run

```shell
 datajob execute --state-machine datajob-python-pyspark-my-stage-workflow
```

## Destroy


```shell
cdk destroy --app "python datajob_stack.py"  -c stage=my-stage
```
