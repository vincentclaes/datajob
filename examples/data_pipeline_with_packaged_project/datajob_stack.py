import pathlib
from aws_cdk import core

from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow


current_dir = pathlib.Path(__file__).parent.absolute()

app = core.App()

# We add the path to the project root in the constructor of DataJobStack.
# By specifying project_root, datajob will look for a .whl in
# the dist folder of your project.
with DataJobStack(
    scope=app, id="data-pipeline-pkg", project_root=current_dir
) as datajob_stack:

    task1 = GlueJob(
        datajob_stack=datajob_stack, name="task1", job_path="glue_jobs/task1.py"
    )

    task2 = GlueJob(
        datajob_stack=datajob_stack, name="task2", job_path="glue_jobs/task2.py"
    )

    with StepfunctionsWorkflow(
        datajob_stack=datajob_stack, name="workflow"
    ) as step_functions_workflow:
        task1 >> task2

app.synth()
