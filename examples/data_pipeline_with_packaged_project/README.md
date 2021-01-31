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

    export AWS_PROFILE=my-profile
    export AWS_DEFAULT_REGION=eu-west-1
    cd examples/data_pipeline_with_packaged_project
    datajob deploy --stage dev --config datajob_stack.py --package
