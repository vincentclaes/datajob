"""same as ./datajob_stack.py but more explicit."""
import pathlib

from aws_cdk import core

from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
from datajob.stepfunctions import StepfunctionsWorkflow

app = core.App()

current_dir = pathlib.Path(__file__).parent.absolute()

app = core.App()

datajob_stack = DataJobStack(
    scope=app, id="data-pipeline-pkg", project_root=current_dir
)
datajob_stack.init_datajob_context()

task1 = GlueJob(
    datajob_stack=datajob_stack, name="task1", job_path="glue_jobs/task1.py"
)
task2 = GlueJob(
    datajob_stack=datajob_stack, name="task2", job_path="glue_jobs/task2.py"
)

with StepfunctionsWorkflow(datajob_stack=datajob_stack, name="workflow") as sfn:
    task1 >> task2

datajob_stack.create_resources()
app.synth()
