# Datajob

#### Build and deploy a serverless data pipeline with no effort on AWS.

- Build and deploy your code to a glue job.
- Package your project as a wheel and make it available for your glue jobs. This enables you to `import my_project` in your glue job.
- Orchestrate your pipeline using stepfunctions as simple as `task1 >> [task2,task3] >> task4`

> The main dependencies are [AWS CDK](https://github.com/aws/aws-cdk) and [Step Functions SDK for data science](https://github.com/aws/aws-step-functions-data-science-sdk-python) <br/>
> Ideas to be implemented can be found [below](#ideas) <br/>
> [Feedback](https://github.com/vincentclaes/datajob/discussions) is much appreciated!


# Installation

 Datajob can be installed using pip. <br/>
 Beware that we depend on [aws cdk cli](https://github.com/aws/aws-cdk)!

    pip install datajob
    npm install -g aws-cdk@1.87.1 # latest version of datajob depends this version

# Quickstart

### Configuration

We have a simple data pipeline composed of 2 glue jobs orchestrated sequentially.
We add the following code in a file called `datajob_stack.py`

```python
import pathlib
from aws_cdk import core

from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow


current_dir = pathlib.Path(__file__).parent.absolute()

app = core.App()

# the datajob_stack is the instance that will result in a cloudformation stack.
# we inject the datajob_stack object through all the resources that we want to add.
with DataJobStack(
    scope=app, id="data-pipeline-pkg", project_root=current_dir
) as datajob_stack:

    # here we define 2 glue jobs with the path to the source code.
    task1 = GlueJob(
        datajob_stack=datajob_stack, name="task1", job_path="glue_jobs/task1.py"
    )

    task2 = GlueJob(
        datajob_stack=datajob_stack, name="task2", job_path="glue_jobs/task2.py"
    )

    # we instantiate a step functions workflow
    # and orchestrate the glue jobs.
    with StepfunctionsWorkflow(datajob_stack=datajob_stack, name="workflow") as sfn:
        task1 >> task2

app.synth()

```

The definition of this pipeline can be found in [`examples/data_pipeline_with_packaged_project/datajob_stack.py`](./examples/data_pipeline_with_packaged_project/datajob_stack.py).

### Configure CDK

We deploy using CDK, therefore we need to set some environment variables
and initialize CDK for our AWS account:

```shell script
export AWS_PROFILE=my-profile # e.g. default
# use the aws cli to get your account number
export AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text --profile $AWS_PROFILE)
export AWS_DEFAULT_REGION=your-region # e.g. eu-west-1

cdk bootstrap aws://$AWS_ACCOUNT/$AWS_DEFAULT_REGION
```

### Deploy

Point to the configuration of the pipeline using `--config` and deploy

```shell script
cd examples/glue_jobs
datajob deploy --config datajob_stack.py --package setuppy
```

After running the `deploy` command, the code of glue jobs are deployed and orchestrated.

### Run

```shell script
datajob execute --state-machine data-pipeline-pkg-dev-workflow
```

### Destroy

Once the pipeline is finished you can pull down the pipeline by using the command:

```shell script
datajob destroy --config datajob_stack.py
```

As simple as that!

> Note: When using datajob cli to deploy a pipeline, we shell out to aws cdk.
> You can circumvent shelling out to aws cdk by running `cdk` explicitly.
> datajob cli prints out the commands it uses in the back to build the pipeline.
> If you want, you can use those.

# Functionality

<details>
<summary>Combine with another cdk stack</summary>
#todo
</details>

<details>
<summary>Package your code as a wheel</summary>
#todo
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
