# Datajob

Build and deploy a serverless data pipeline with no effort on AWS.

# Installation
    
    pip install datajob
    # We depend on AWS CDK.
    npm install -g aws-cdk

# Create a pipeline

see the full example in `examples/simple_data_pipeline`

    from datajob.datajob_stack import DataJobStack
    from datajob.glue.glue_job import GlueJob
    from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow
    import pathlib
    
    current_dir = pathlib.Path(__file__).parent.absolute()
    
    with DataJobStack(
        stack_name="simple-data-pipeline", project_root=current_dir
    ) as datajob_stack:
        task1 = GlueJob(
            datajob_stack=datajob_stack,
            name="task1",
            path_to_glue_job="simple_data_pipeline/task1.py",
        )
        task2 = GlueJob(
            datajob_stack=datajob_stack,
            name="task2",
            path_to_glue_job="simple_data_pipeline/task2.py",
        )
        task3 = GlueJob(
            datajob_stack=datajob_stack,
            name="task3",
            path_to_glue_job="simple_data_pipeline/task3.py",
        )
    
        with StepfunctionsWorkflow(
            datajob_stack=datajob_stack,
            name="simple-data-pipeline",
        ) as sfn:
            [task1, task2] >> task3

        
save this code in a file called `datajob_stack.py` in the root of your project

## Deploy a pipeline

    export AWS_DEFAULT_ACCOUNT=077590795309
    export AWS_PROFILE=my-profile
    cd examples/simple_data_pipeline
    datajob deploy --stage dev --config datajob_stack.py --package