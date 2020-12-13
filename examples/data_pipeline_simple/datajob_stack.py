from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow


# the datajob_stack is the instance that will result in a cloudformation stack.
# we inject the datajob_stack object through all the resources that we want to add.
with DataJobStack(stack_name="data-pipeline-simple") as datajob_stack:

    # here we define 3 glue jobs with the datajob_stack object,
    # a name and the relative path to the source code.
    task1 = GlueJob(
        datajob_stack=datajob_stack,
        name="task1",
        job_path="data_pipeline_simple/task1.py",
    )
    task2 = GlueJob(
        datajob_stack=datajob_stack,
        name="task2",
        job_path="data_pipeline_simple/task2.py",
    )
    task3 = GlueJob(
        datajob_stack=datajob_stack,
        name="task3",
        job_path="data_pipeline_simple/task3.py",
    )

    # we instantiate a step functions workflow and add the sources
    # we want to orchestrate. We got the orchestration idea from
    # airflow where we use a list to run tasks in parallel
    # and we use bit operator '>>' to chain the tasks in our workflow.
    with StepfunctionsWorkflow(
        datajob_stack=datajob_stack, name="data-pipeline-simple"
    ) as sfn:
        [task1, task2] >> task3

# to package and deploy this stack execute
# cdk deploy --app  "python datajob_stack.py"  -c stage=dev
# or use the datajob cli
# datajob deploy --stage dev --config datajob_stack.py
