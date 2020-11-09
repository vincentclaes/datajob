# DATAJOB

Build and deploy a serverless data pipeline with no effort.

# Installation
    
    pip install datajob
    # We depend on the AWS CDK.
    npm install -g aws-cdk

# Create and deploy a pipeline

    from datajob.datajob_stack import DataJobStack
    from datajob.glue.glue_job import GlueJob
    
    with DataJobStack(stack_name="simple-data-pipeline", stage="dev") as datajob_stack:
        datajob_stack.add(
            GlueJob(
                scope=datajob_stack,
                glue_job_name="task1",
                stage=datajob_stack.stage,
                path_to_glue_job="glue/task1.py",
            )
        )
        
save this code in a file called `datajob_stack.py`

to deploy execute:

    export AWS_DEFAULT_ACCOUNT=077590795309
    export AWS_PROFILE=my-profile
    cdk deploy --app "python datajob_stack.py"