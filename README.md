# Datajob

Build and deploy a serverless data pipeline with no effort on AWS.

currently we support;

- packaging and deploying glue jobs
- orchestrating glue jobs using stepfunctions

any suggestions can be shared by creating an [issue](https://github.com/vincentclaes/datajob/issues)

# Installation
 
 datajob can be installed using pip. Beware that we depend on [aws cdk cli](https://github.com/aws/aws-cdk)!
    
    pip install datajob
    npm install -g aws-cdk

# Create a pipeline
    
see the full example in [examples/data_pipeline_simple](https://github.com/vincentclaes/datajob/tree/add-simple-example/examples/data_pipeline_simple)

- The idea is that you create a [`DataJobStack`](https://github.com/vincentclaes/datajob/blob/add-simple-example/datajob/datajob_stack.py) as and that you assign it one or more `GlueJob`.
- Each [`GlueJob`](https://github.com/vincentclaes/datajob/blob/add-simple-example/datajob/glue/glue_job.py) has at least a name, a path to the glue job and takes a `DataJobStack` instance as argument.
- We can orchestrate our glue jobs using a [`StepfunctionsWorkflow`](https://github.com/vincentclaes/datajob/blob/add-simple-example/datajob/stepfunctions/stepfunctions_workflow.py) where we define our jobs as sequential or as parallel. 


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


        
save this code in a file called `datajob_stack.py` in the root of your project

## Deploy a pipeline

    export AWS_DEFAULT_ACCOUNT=my-account-number
    export AWS_PROFILE=my-profile
    cd examples/data_pipeline_simple
    datajob deploy --stage dev --config datajob_stack.py