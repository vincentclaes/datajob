# Datajob

#### Build and deploy a serverless data pipeline with no effort on AWS.

- Build and deploy your code to a glue job.
- Package your project as a wheel and make it available for your glue jobs. This enables you to `import my_project` in your glue job.
- Orchestrate your pipeline using stepfunctions as simple as `task1 >> [task2,task3] >> task4`

> Dependencies are [AWS CDK](https://github.com/aws/aws-cdk) and [Step Functions SDK for data science](https://github.com/aws/aws-step-functions-data-science-sdk-python) <br/>

# Installation

 Datajob can be installed using pip. <br/>
 Beware that we depend on [aws cdk cli](https://github.com/aws/aws-cdk)!

    pip install datajob
    npm install -g aws-cdk@1.87.1 # latest version of datajob depends this version

# Quickstart

### Configuration

We have a simple data pipeline composed of 2 glue jobs orchestrated sequentially.

```python
from aws_cdk import core

from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow

app = core.App()

# The datajob_stack is the instance that will result in a cloudformation stack.
# We inject the datajob_stack object through all the resources that we want to add.
with DataJobStack(scope=app, id="data-pipeline-simple") as datajob_stack:

    # We define 2 glue jobs with the relative path to the source code.
    task1 = GlueJob(
        datajob_stack=datajob_stack, name="task1", job_path="glue_jobs/task1.py"
    )
    task2 = GlueJob(
        datajob_stack=datajob_stack, name="task2", job_path="glue_jobs/task2.py"
    )

    # We instantiate a step functions workflow and orchestrate the glue jobs.
    with StepfunctionsWorkflow(datajob_stack=datajob_stack, name="workflow") as sfn:
        task1 >> task2

app.synth()

```

We add the code in a file called `datajob_stack.py` in the [root of the project](./examples/data_pipeline_simple/).


### Configure CDK

```shell script
export AWS_PROFILE=my-profile # e.g. default
# use the aws cli to get your account number
export AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text --profile $AWS_PROFILE)
export AWS_DEFAULT_REGION=your-region # e.g. eu-west-1

cdk bootstrap aws://$AWS_ACCOUNT/$AWS_DEFAULT_REGION
```

### Deploy
_cdk cli_

```shell script
cd examples/data_pipeline_simple
python setup.py bdist_wheel
cdk deploy --app  "python datajob_stack.py"
```

_datajob cli_

```shell script
cd examples/data_pipeline_simple
datajob deploy --config datajob_stack.py --package setuppy
```

After running the `deploy` command, the code of glue jobs are deployed and orchestrated.

### Run

```shell script
datajob execute --state-machine data-pipeline-simple-dev-workflow
```

### Destroy
_cdk cli_
```shell script
cdk destroy --app  "python datajob_stack.py"
```

_datajob cli_
```shell script
datajob destroy --config datajob_stack.py
```

# Functionality

<details>
<summary>Pass arguments to a glue job</summary>
#todo implemented not documented
</details>

<details>
<summary>Deploy files to deployment bucket</summary>
#todo implemented not documented
</details>

<details>
<summary>Package project</summary>
#todo implemented not documented
</details>

<details>
<summary>Using Pyspark</summary>
#todo implemented not documented
</details>

<details>
<summary>Using S3 bucket to dump data</summary>
#todo implemented not documented
# create an example that dumps and reads from s3
</details>

<details>
<summary>Orchestrate Stepfunctions in parallel</summary>
#todo
# orchestrate in parallel
</details>

<details>
<summary>Orchestrate 1 Stepfunction</summary>
#todo
# orchestrate 1 job
</details>


# The magic behind datajob

```python
with DataJobStack(scope=app, id="data-pipeline-simple") as datajob_stack:
    ...
```

When __entering the contextmanager__ of DataJobStack:

A [DataJobContext](./datajob/datajob_stack.py#L48) is initialized
which provides context in to deploy run a data pipeline on AWS.
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
from aws_cdk import core

from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow

app = core.App()

datajob_stack = DataJobStack(scope=app, id="data-pipeline-simple")
datajob_stack.init_datajob_context()

task1 = GlueJob(datajob_stack=datajob_stack, name="task1", job_path="glue_jobs/task1.py")
task2 = GlueJob(datajob_stack=datajob_stack, name="task2", job_path="glue_jobs/task2.py")

with StepfunctionsWorkflow(datajob_stack=datajob_stack, name="workflow") as sfn:
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
    - create sagemaker model
    - create sagemaker endpoint
    - expose sagemaker endpoint to the internet by levering lambda + api gateway

- create a serverless UI that follows up on the different pipelines deployed on possibly different AWS accounts using Datajob

> [Feedback](https://github.com/vincentclaes/datajob/discussions) is much appreciated!
