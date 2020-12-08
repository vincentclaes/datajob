# Datajob

Build and deploy a serverless data pipeline with no effort on AWS.

- Create and deploy glue jobs
- Package your project and make it available on AWS
- Orchestrate your pipeline using stepfunctions as simple as `task1 >> [task2,task3] >> task4`

Any suggestions can be shared by creating an [issue](https://github.com/vincentclaes/datajob/issues)

# Installation

 datajob can be installed using pip. Beware that we depend on [aws cdk cli](https://github.com/aws/aws-cdk)!

    pip install datajob
    npm install -g aws-cdk

# Example
See the full example [here](https://github.com/vincentclaes/datajob/tree/add-simple-example/examples/data_pipeline_simple)

## Create a pipeline

The code below is saved in the root of your project in a file called `datajob_stack.py`


      from datajob.datajob_stack import DataJobStack
      from datajob.glue.glue_job import GlueJob
      from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow


      with DataJobStack(stack_name="data-pipeline-simple") as datajob_stack:

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

      with StepfunctionsWorkflow(
          datajob_stack=datajob_stack,
          name="data-pipeline-simple",
      ) as sfn:
          [task1, task2] >> task3

- The idea is that you create a [`DataJobStack`](https://github.com/vincentclaes/datajob/blob/add-simple-example/datajob/datajob_stack.py) and that you assign it some resources; one or more `GlueJob` and a `StepfunctionsWorkflow`.
    - The instance of `DataJobStack` in the example is `datajob_stack`

- Each [`GlueJob`](https://github.com/vincentclaes/datajob/blob/add-simple-example/datajob/glue/glue_job.py) has at least a name, a path to the glue job and takes a `DataJobStack` instance as argument.
    - In our example we have 3 `GlueJob` called `task1`, `task2`, `task3`
    - You can find the code for the glue jobs [here](https://github.com/vincentclaes/datajob/tree/main/examples/data_pipeline_simple/data_pipeline_simple)

- We can orchestrate our glue jobs using a [`StepfunctionsWorkflow`](https://github.com/vincentclaes/datajob/blob/add-simple-example/datajob/stepfunctions/stepfunctions_workflow.py), where we orchestrate our `GlueJob` sequentially or in parallel.
    - The instance of `StepfunctionsWorkflow` is called `sfn` and it orchestrates `task1`, `task2` in parallel and starts `task3` only when task1 and task2 both are finished.


## Deploy a pipeline

Deploy your pipeline using a unique identifier `--stage` and point to the configuration of the pipeline using `--config`
Execute the following commands to deploy our example:

    export AWS_DEFAULT_ACCOUNT=my-account-number
    export AWS_PROFILE=my-profile
    cd examples/data_pipeline_simple
    datajob deploy --stage dev --config datajob_stack.py

> Note: When using datajob cli to deploy your pipline, we shell out to aws cdk.
> You can circumvent shelling out to aws cdk by running `cdk` explicitly

# Local development

clone the repo andd execute:

    make install
