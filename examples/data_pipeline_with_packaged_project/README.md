# Data pipeline with packaged project

It might be that you would like to package your project and ship it with your glue job.
in order to do that make sure you;

Specify the absolute path in the root of your project.

    ```
    current_dir = pathlib.Path(__file__).parent.absolute()

    with DataJobStack(
        stack_name="simple-data-pipeline", project_root=current_dir
    )
    ```

Make sure you have configured a `setup.py` in the root of your poject.

## Deployment

    git clone git@github.com:vincentclaes/datajob.git
    cd datajob

    pip install poetry --upgrade
    poetry shell
    poetry install

    cd examples/data_pipeline_with_packaged_project
    export AWS_PROFILE=default
    export AWS_DEFAULT_REGION=eu-west-1
    export AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text --profile $AWS_PROFILE)

    cdk bootstrap aws://$AWS_ACCOUNT/$AWS_DEFAULT_REGION

    # if you want to create a wheel from setup.py and create the services
    # and deploy the packaged dependencies
    python setup.py bdist_wheel
    cdk deploy --app "python datajob_stack.py"

    # to execute the pipeline, pass the name of the step functions statemachine
    # which is the same as the name of the stack in this case.
    datajob execute data-pipeline-pkg-dev-workflow

## Remarks

You can try with the datajob cli to package before deploying.
Doing everything with one command.

    datajob deploy --config datajob_stack.py --package setuppy

You can also use the datajob cli to package using poetry

    datajob deploy --config datajob_stack.py --package poetry
