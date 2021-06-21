# Data pipeline simple

A simple data pipeline with 3 tasks where the tasks are executed both sequentially and in parallel.
The tasks are glue pythonshell jobs and they are orchestrated using step functions.

The definition of the datajob can be found in `datajob_stack.py`


# Deployment

    export AWS_PROFILE=my-profile
    export AWS_DEFAULT_REGION=eu-west-1
    cd examples/data_pipeline_simple
    cdk deploy --app  "python datajob_stack.py"
    datajob execute --state-machine data-pipeline-simple-dev-workflow
