import pathlib

from aws_cdk import core

from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
from datajob.stepfunctions import StepfunctionsWorkflow

current_dir = str(pathlib.Path(__file__).parent.absolute())

app = core.App()

with DataJobStack(
    scope=app, id="datajob-python-pyspark", project_root=current_dir
) as datajob_stack:

    pyspark_job = GlueJob(
        datajob_stack=datajob_stack,
        name="pyspark-job",
        job_path="glue_job/glue_pyspark_example.py",
        job_type="glueetl",
        glue_version="2.0",  # we only support glue 2.0
        python_version="3",
        worker_type="Standard",  # options are Standard / G.1X / G.2X
        number_of_workers=1,
        arguments={
            "--source": f"s3://{datajob_stack.context.data_bucket_name}/raw/iris_dataset.csv",
            "--destination": f"s3://{datajob_stack.context.data_bucket_name}/target/pyspark_job/iris_dataset.parquet",
        },
    )

    with StepfunctionsWorkflow(datajob_stack=datajob_stack, name="workflow") as sfn:
        pyspark_job >> ...
