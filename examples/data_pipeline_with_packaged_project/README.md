# Data pipeline with packaged project

Often you would like to package your project and ship it with your glue job.
in order to do that make sure you;

1) Specify the absolute path to the root of your project.
    
    current_dir = pathlib.Path(__file__).parent.absolute()
    
    with DataJobStack(
        stack_name="simple-data-pipeline", project_root=current_dir
    )
  
2) Make sure you have configured a `setup.py` in the root of your poject.

to deploy:

    export AWS_DEFAULT_ACCOUNT=my-account-number
    export AWS_PROFILE=my-profile
    cd examples/data_pipeline_with_packaged_project
    datajob deploy --stage dev --config datajob_stack.py