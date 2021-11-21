# Data pipeline parallel

Orchestrate tasks in parallel. For more info look in `datajob_stack.py`

# Deployment

    git clone git@github.com:vincentclaes/datajob.git
    cd datajob

    pip install poetry --upgrade
    poetry shell
    poetry install

    cd examples/data_pipeline_parallel
    export AWS_PROFILE=default
    export AWS_DEFAULT_REGION=eu-west-1
    export AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text --profile $AWS_PROFILE)

    cdk bootstrap aws://$AWS_ACCOUNT/$AWS_DEFAULT_REGION
    cdk deploy --app "python datajob_stack.py" --require-approval never


# Run

    datajob execute --state-machine data-pipeline-parallel-workflow
