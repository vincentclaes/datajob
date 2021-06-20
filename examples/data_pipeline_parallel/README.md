# Data pipeline parallel

Orchestrate tasks in parallel. For more info look in `datajob_stack.py`

# Deployment

    export AWS_PROFILE=my-profile
    export AWS_DEFAULT_REGION=eu-west-1
    cd examples/data_pipeline_parallel
    datajob deploy --config datajob_stack.py
    datajob execute --state-machine data-pipeline-parallel-workflow
