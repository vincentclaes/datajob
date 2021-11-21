# Data pipeline simple

A simple data pipeline with 3 tasks where the tasks are executed both sequentially and in parallel.
The tasks are glue pythonshell jobs and they are orchestrated using step functions.

The definition of the datajob can be found in `datajob_stack.py`


## Deployment

    git clone git@github.com:vincentclaes/datajob.git
    cd datajob

    pip install poetry --upgrade
    poetry shell
    poetry install

    cd examples/data_pipeline_simple
    export AWS_PROFILE=default
    export AWS_DEFAULT_REGION=eu-west-1
    export AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text --profile $AWS_PROFILE)

    cdk bootstrap aws://$AWS_ACCOUNT/$AWS_DEFAULT_REGION
    cdk deploy --app  "python datajob_stack.py" --require-approval never

             ✅  data-pipeline-simple

            Stack ARN:
            arn:aws:cloudformation:eu-west-1:-----:stack/data-pipeline-simple/39be7bb0-4adf-11ec-a1ad-02c674726183

## Execute

    datajob execute --state-machine data-pipeline-simple-workflow

            [16:28:56] executing: data-pipeline-simple-workflow
            [16:28:58] status: RUNNING
                view the execution on the AWS console:

            https://console.aws.amazon.com/states/home?region=eu-west-1#/executions/details/arn:aws:states:eu-west-1:-------:execution:data-pipeline-simple-workflow:e995da1a-ad0e-44f6-997b-e7a229eaf024

If you click the link, you can follow up on the progress

## Destroy

    cdk destroy --app  "python datajob_stack.py"
