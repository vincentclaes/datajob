# Data pipeline simple

a simple data pipeline with 3 tasks that are executed sequentially and in parallel.

    export AWS_DEFAULT_ACCOUNT=my-account-number
    export AWS_PROFILE=my-profile
    cd examples/data_pipeline_simple
    datajob deploy --stage dev --config datajob_stack.py