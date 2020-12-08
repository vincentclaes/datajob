from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow


with DataJobStack(stack_name="data-pipeline-simple") as datajob_stack:
    task1 = GlueJob(
        datajob_stack=datajob_stack,
        name="task1",
        path_to_glue_job="data_pipeline_simple/task1.py",
    )
    task2 = GlueJob(
        datajob_stack=datajob_stack,
        name="task2",
        path_to_glue_job="data_pipeline_simple/task2.py",
    )
    task3 = GlueJob(
        datajob_stack=datajob_stack,
        name="task3",
        path_to_glue_job="data_pipeline_simple/task3.py",
    )

    with StepfunctionsWorkflow(
        datajob_stack=datajob_stack,
        name="data-pipeline-simple",
    ) as sfn:
        [task1, task2] >> task3
