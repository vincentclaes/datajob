# Datajob

#### Build and deploy a serverless data pipeline on AWS with no effort.

- We support python shell / pyspark Glue jobs.
- Orchestrate using stepfunctions as simple as `task1 >> [task2,task3] >> task4`
- Let us [know](https://github.com/vincentclaes/datajob/discussions) what you want to see next.

> Dependencies are [AWS CDK](https://github.com/aws/aws-cdk) and [Step Functions SDK for data science](https://github.com/aws/aws-step-functions-data-science-sdk-python) <br/>

# Installation

 Datajob can be installed using pip. <br/>
 Beware that we depend on [aws cdk cli](https://github.com/aws/aws-cdk)!

    pip install datajob
    npm install -g aws-cdk@1.87.1 # latest version of datajob depends this version

# Quickstart

We have a simple data pipeline composed of [2 glue jobs](./examples/data_pipeline_with_packaged_project/glue_jobs/) orchestrated sequentially using step functions.

```python
import pathlib
from aws_cdk import core

from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow


current_dir = pathlib.Path(__file__).parent.absolute()

app = core.App()


with DataJobStack(
    scope=app, id="data-pipeline-pkg", project_root=current_dir
) as datajob_stack:

    task1 = GlueJob(
        datajob_stack=datajob_stack, name="task1", job_path="glue_jobs/task1.py"
    )

    task2 = GlueJob(
        datajob_stack=datajob_stack, name="task2", job_path="glue_jobs/task2.py"
    )

    with StepfunctionsWorkflow(datajob_stack=datajob_stack, name="workflow") as step_functions_workflow:
        task1 >> task2

app.synth()

```

We add the above code in a file called `datajob_stack.py` in the [root of the project](./examples/data_pipeline_with_packaged_project/).


### Configure CDK
Follow the steps [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-config) to configure your credentials.

```shell script
export AWS_PROFILE=my-profile # e.g. default
# use the aws cli to get your account number
export AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text --profile $AWS_PROFILE)
export AWS_DEFAULT_REGION=your-region # e.g. eu-west-1

cdk bootstrap aws://$AWS_ACCOUNT/$AWS_DEFAULT_REGION
```

### Deploy

Datajob will create s3 buckets based on the `datajob_stack.id` and the `stage` variable.
The stage variable will typically be something like "dev", "stg", "prd", ...
but since S3 buckets need to be globally unique, for this example we will use our `$AWS_ACCOUNT` for the `--stage` parameter.

```shell
export STAGE=$AWS_ACCOUNT
```

Navigate to `datajob_stack.py` file and deploy the data pipeline.

```shell script
cd examples/data_pipeline_with_packaged_project
datajob deploy --config datajob_stack.py --stage $STAGE --package setuppy
```

<details>
<summary>use cdk cli</summary>

```shell script
cd examples/data_pipeline_with_packaged_project
python setup.py bdist_wheel
cdk deploy --app  "python datajob_stack.py" -c stage=$STAGE
```
</details>

Your glue jobs are deployed and the orchestration is configured.

### Run

The step function state machine name is constructed as `<datajob_stack.id>-<stage>-<step_functions_workflow.name>`.

To run your data pipeline execute:

```shell script
datajob execute --state-machine data-pipeline-pkg-$STAGE-workflow
```
The terminal will output a link to the step functions page to follow up on your pipeline run.

### Destroy

```shell script
datajob destroy --config datajob_stack.py --stage $STAGE
```

<details>
<summary>use cdk cli</summary>
```shell script
cdk destroy --app  "python datajob_stack.py" -c stage=$STAGE
```
</details>

> Note: you can use any cdk arguments in the datajob cli

# Functionality

<details>
<summary>Using datajob's S3 data bucket</summary>

Pass arguments to your Glue job using the `arguments` parameter and
dynamically reference the `datajob_stack` data bucket name for this `stage` to the arguments.

```python
import pathlib

from aws_cdk import core
from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow

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

```

deploy to stage `my-stage`:

```shell
datajob deploy --config datajob_stack.py --stage my-stage --package setuppy
```

`datajob_stack.context.data_bucket_name` will evaluate to `datajob-python-pyspark-my-stage

you can find this example [here](./examples/data_pipeline_pyspark/glue_job/glue_pyspark_example.py)

</details>

<details>
<summary>Deploy files to deployment bucket</summary>

Specify the path to the folder we would like to include in the deployment bucket.

```python

from aws_cdk import core
from datajob.datajob_stack import DataJobStack

app = core.App()

with DataJobStack(
    scope=app, id="some-stack-name", include_folder="path/to/folder/"
) as datajob_stack:

    ...

```

</details>

<details>
<summary>Package project</summary>

Package you project using [poetry](https://python-poetry.org/)

```shell
datajob deploy --config datajob_stack.py --package poetry
```
Package you project using [setup.py](./examples/data_pipeline_with_packaged_project)
```shell
datajob deploy --config datajob_stack.py --package setuppy
```
</details>

<details>
<summary>Using Pyspark</summary>

```python
import pathlib

from aws_cdk import core
from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow

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
```
full example can be found in [examples/data_pipeline_pyspark](examples/data_pipeline_pyspark]).
</details>

<details>
<summary>Using datajob's S3 data bucket</summary>


```python

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

```


</details>

<details>
<summary>Orchestrate stepfunctions tasks in parallel</summary>

```python
# task1 and task2 are orchestrated in parallel.
# task3 will only start when both task1 and task2 have succeeded.
[task1, task2] >> task3
```

</details>

<details>
<summary>Orchestrate 1 stepfunction task</summary>

Use the [Ellipsis](https://docs.python.org/dev/library/constants.html#Ellipsis) object to be able to orchestrate 1 job via step functions.

```python
some_task >> ...
```

</details>


# Datajob in depth

The `datajob_stack` is the instance that will result in a cloudformation stack.
The path in `project_root` helps datajob_stack locate the root of the project where
the setup.py/poetry pyproject.toml file can be found as well as the `dist/` folder with the wheel of your project .

```python
import pathlib
from aws_cdk import core

from datajob.datajob_stack import DataJobStack

current_dir = pathlib.Path(__file__).parent.absolute()
app = core.App()

with DataJobStack(
    scope=app, id="data-pipeline-pkg", project_root=current_dir
) as datajob_stack:

    ...
```

When __entering the contextmanager__ of DataJobStack:

A [DataJobContext](./datajob/datajob_stack.py#L48) is initialized
to deploy and run a data pipeline on AWS.
The following resources are created:
1) "data bucket"
    - an S3 bucket that you can use to dump ingested data, dump intermediate results and the final output.
    - you can access the data bucket as a [Bucket](https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_s3/Bucket.html) object via ```datajob_stack.context.data_bucket```
    - you can access the data bucket name via ```datajob_stack.context.data_bucket_name```
2) "deployment bucket"
   - an s3 bucket to deploy code, artifacts, scripts, config, files, ...
   - you can access the deployment bucket as a [Bucket](https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_s3/Bucket.html) object via ```datajob_stack.context.deployment_bucket```
   - you can access the deployment bucket name via ```datajob_stack.context.deployment_bucket_name```

when __exiting the context manager__ all the resources of our DataJobStack object are created.

<details>
<summary>We can write the above example more explicitly...</summary>

```python
import pathlib
from aws_cdk import core

from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow

app = core.App()

current_dir = pathlib.Path(__file__).parent.absolute()

app = core.App()

datajob_stack = DataJobStack(scope=app, id="data-pipeline-pkg", project_root=current_dir)
datajob_stack.init_datajob_context()

task1 = GlueJob(datajob_stack=datajob_stack, name="task1", job_path="glue_jobs/task1.py")
task2 = GlueJob(datajob_stack=datajob_stack, name="task2", job_path="glue_jobs/task2.py")

with StepfunctionsWorkflow(datajob_stack=datajob_stack, name="workflow") as step_functions_workflow:
    task1 >> task2

datajob_stack.create_resources()
app.synth()
```
</details>

# Ideas

Any suggestions can be shared by starting a [discussion](https://github.com/vincentclaes/datajob/discussions)

These are the ideas, we find interesting to implement;

- add a time based trigger to the step functions workflow.
- add an s3 event trigger to the step functions workflow.
- add a lambda that copies data from one s3 location to another.
- add an sns that notifies in case of any failure (slack/email)
- version your data pipeline.
- cli command to view the logs / glue jobs / s3 bucket
- implement sagemaker services
    - processing jobs
    - hyperparameter tuning jobs
    - training jobs
- implement lambda
- implement ECS Fargate
- create a serverless UI that follows up on the different pipelines deployed on possibly different AWS accounts using Datajob

> [Feedback](https://github.com/vincentclaes/datajob/discussions) is much appreciated!
