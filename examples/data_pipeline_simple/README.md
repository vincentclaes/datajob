# Data pipeline simple

A simple data pipeline with 3 tasks where the tasks are executed both sequentially and in parallel.
The tasks are glue pythonshell jobs and they are orchestrated using step functions.

The definition of the datajob can be found [here](https://github.com/vincentclaes/datajob/blob/add-simple-example/examples/data_pipeline_simple/datajob_stack.py)


# Deployment

    export AWS_DEFAULT_ACCOUNT=my-account-number
    export AWS_PROFILE=my-profile
    cd examples/data_pipeline_simple
    datajob deploy --stage dev --config datajob_stack.py
