from aws_cdk import core

from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow

app = core.App()

# The datajob_stack is the instance that will result in a cloudformation stack.
# We inject the datajob_stack object through all the resources that we want to add.
with DataJobStack(scope=app, id="data-pipeline-simple") as datajob_stack:

    # We define 2 glue jobs with the relative path to the source code.
    task1 = GlueJob(
        datajob_stack=datajob_stack, name="task1", job_path="glue_jobs/task1.py"
    )
    task2 = GlueJob(
        datajob_stack=datajob_stack, name="task2", job_path="glue_jobs/task2.py"
    )

    # We instantiate a step functions workflow and orchestrate the glue jobs.
    with StepfunctionsWorkflow(datajob_stack=datajob_stack, name="workflow") as sfn:
        task1 >> task2

app.synth()
