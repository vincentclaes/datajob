from aws_cdk import core

from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow

app = core.App()


with DataJobStack(scope=app, id="data-pipeline-simple") as datajob_stack:

    task1 = GlueJob(
        datajob_stack=datajob_stack, name="task1", job_path="glue_jobs/task.py"
    )
    task2 = GlueJob(
        datajob_stack=datajob_stack, name="task2", job_path="glue_jobs/task.py"
    )
    task3 = GlueJob(
        datajob_stack=datajob_stack, name="task3", job_path="glue_jobs/task.py"
    )
    task4 = GlueJob(
        datajob_stack=datajob_stack, name="task4", job_path="glue_jobs/task.py"
    )
    task5 = GlueJob(
        datajob_stack=datajob_stack, name="task5", job_path="glue_jobs/task.py"
    )

    # Task2 comes after task1. task4 comes after task3.
    # Task 5 depends on both task2 and task4 to be finished.
    # Therefore task1 and task2 can run in parallel,
    # as well as task3 and task4.
    with StepfunctionsWorkflow(datajob_stack=datajob_stack, name="workflow") as sfn:
        task1 >> task2
        task3 >> task4
        task2 >> task5
        task4 >> task5

app.synth()
