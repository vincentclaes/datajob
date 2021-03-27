# Data Pipeline Pyspark

we have 2 a [pyspark job](./glue_job/glue_pyspark_example.py) that:

- reads the dataset `iris_dataset.csv` from s3
- dumps the result back to s3 as a parquet file


## Deploy

```shell
export AWS_PROFILE=my-profile
```

```shell
datajob deploy --config datajob_stack.py --stage my-stage --package setuppy
```
or

```shell
python setup.py bdist_wheel
cdk deploy --app "python datajob_stack.py"  -c stage=my-stage
```

```shell
aws s3 cp ./dataset/iris_dataset.csv s3://datajob-python-pyspark-my-stage/raw/iris_dataset.csv
```

## Run

```shell
 datajob execute --state-machine datajob-python-pyspark-my-stage-workflow
```

## Destroy

```shell
datajob destroy --config datajob_stack.py --stage my-stage
```
or

```shell
cdk destroy --app "python datajob_stack.py"  -c stage=my-stage
```
