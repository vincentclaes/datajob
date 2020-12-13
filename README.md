# Datajob

Build and deploy a serverless data pipeline with no effort on AWS.

- Deploy your code to a glue job
- Package your project and make it available on AWS
- Orchestrate your pipeline using stepfunctions as simple as `task1 >> [task2,task3] >> task4`

# Installation

 datajob can be installed using pip. Beware that we depend on [aws cdk cli](https://github.com/aws/aws-cdk)!

    pip install datajob
    npm install -g aws-cdk

# Example

A simple data pipeline with 3 Glue python shell tasks that are executed both sequentially and in parallel.
See the full example [here](https://github.com/vincentclaes/datajob/tree/main/examples/data_pipeline_simple)

    from datajob.datajob_stack import DataJobStack
    from datajob.glue.glue_job import GlueJob
    from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow


    # the datajob_stack is the instance that will result in a cloudformation stack.
    # we inject the datajob_stack object through all the resources that we want to add.
    with DataJobStack(stack_name="data-pipeline-simple") as datajob_stack:

        # here we define 3 glue jobs with the datajob_stack object,
        # a name and the relative path to the source code.
        task1 = GlueJob(
            datajob_stack=datajob_stack,
            name="task1",
            path_to_glue_job="data_pipeline_simple/task1.py",
        )
        task2 = GlueJob(
            datajob_stack=datajob_stack,
            name="task2",
            path_to_glue_job="data_pipeline_simple/task2.py",
        )
        task3 = GlueJob(
            datajob_stack=datajob_stack,
            name="task3",
            path_to_glue_job="data_pipeline_simple/task3.py",
        )

        # we instantiate a step functions workflow and add the sources
        # we want to orchestrate. We got the orchestration idea from
        # airflow where we use a list to run tasks in parallel
        # and we use bit operator '>>' to chain the tasks in our workflow.
        with StepfunctionsWorkflow(
            datajob_stack=datajob_stack,
            name="data-pipeline-simple",
        ) as sfn:
            [task1, task2] >> task3


## Deploy and destroy

Deploy your pipeline using a unique identifier `--stage` and point to the configuration of the pipeline using `--config`

    export AWS_DEFAULT_ACCOUNT=my-account-number
    export AWS_PROFILE=my-profile
    cd examples/data_pipeline_simple
    datajob deploy --stage dev --config datajob_stack.py
    datajob destroy --stage dev --config datajob_stack.py


> Note: When using datajob cli to deploy a pipeline, we shell out to aws cdk.
> You can circumvent shelling out to aws cdk by running `cdk` explicitly.
> datajob cli prints out the commands it uses in the back to build the pipeline.
> If you want, you can use those.

    cd examples/data_pipeline_simple
    cdk deploy --app  "python datajob_stack.py"  -c stage=dev
    cdk destroy --app  "python datajob_stack.py"  -c stage=dev

# Ideas

- trigger a pipeline using the cli; `datajob run --pipeline my-simple-pipeline`
- implement a data bucket, that's used for your pipeline.
- add a time based trigger to the step functions workflow.
- add an s3 event trigger to the step functions workflow.
- add a lambda that copies data from one s3 location to another.
- version your data pipeline.
- implement sagemaker services
    - processing jobs
    - hyperparameter tuning jobs
    - training jobs
    - create sagemaker model
    - create sagemaker endpoint
    - expose sagemaker endpoint to the internet by levering lambda + api gateway

Any suggestions can be shared by starting a [discussion](https://github.com/vincentclaes/datajob/discussions)
