from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow
import pathlib

current_dir = pathlib.Path(__file__).parent.absolute()

with DataJobStack(
    stack_name="simple-data-pipeline", stage="dev", project_root=current_dir
) as datajob_stack:
    task1 = GlueJob(
        datajob_stack=datajob_stack,
        name="task1",
        path_to_glue_job="simple_data_pipeline/task1.py",
    )
    task2 = GlueJob(
        datajob_stack=datajob_stack,
        name="task2",
        path_to_glue_job="simple_data_pipeline/task2.py",
    )
    task3 = GlueJob(
        datajob_stack=datajob_stack,
        name="task3",
        path_to_glue_job="simple_data_pipeline/task3.py",
    )

    with StepfunctionsWorkflow(datajob_stack=datajob_stack, name="simple-data-pipeline", role_arn="arn:aws:iam::077590795309:role/stepfunctions-datajob"):
        [task1, task2] >> task3