# ML Pipeline Scikitlearn

An ML pipeline that has a preprocessing step, a training step and a step to create a sagemaker model.

## Deploy

    git clone git@github.com:vincentclaes/datajob.git
    cd datajob

    pip install poetry --upgrade
    poetry shell
    poetry install

    cd examples/ml_pipeline_sagemaker_scikitlearn
    export AWS_PROFILE=my-profile
    export AWS_DEFAULT_REGION=eu-west-1
    export AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text --profile $AWS_PROFILE)

    cdk bootstrap aws://$AWS_ACCOUNT/$AWS_DEFAULT_REGION
    cdk deploy --app "python datajob_stack.py" --require-approval never

execute the ml pipeline

    datajob execute --state-machine datajob-ml-pipeline-scikitlearn-workflow

            [13:48:27] execution input found:
                       {'datajob-ml-pipeline-scikitlearn-processing-job': 'datajob-ml-pipeline-scikitlearn-processing-job-20210803T114826',
                       'datajob-ml-pipeline-scikitlearn-training-job': 'datajob-ml-pipeline-scikitlearn-training-job-20210803T114826',
                       'datajob-ml-pipeline-scikitlearn-create-model': 'datajob-ml-pipeline-scikitlearn-create-model-20210803T114826'}
                       executing: datajob-ml-pipeline-scikitlearn-workflow
            [13:48:28] status: RUNNING
                       view the execution on the AWS console:

            https://console.aws.amazon.com/states/home?region=eu-west-1#/executions/details/arn:aws:states:eu-west-1:1234567890:execution:datajob-ml-pipeline-scikitlearn-workflow:fa820474-0fd4-4650-8a96-47d14edcf298

If you click the link, you can follow up on the progress

![stepfunctions-workflow](./assets/stepfunctions-workflow.png)

In the end a sagemaker model is created that you can use behind a sagemaker endpoint.
