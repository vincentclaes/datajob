from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
import pathlib

current_dir = pathlib.Path(__file__).parent.absolute()

with DataJobStack(
    stack_name="simple-data-pipeline", stage="dev", project_root=current_dir
) as datajob_stack:
        GlueJob(
            datajob_stack=datajob_stack,
            glue_job_name="task1",
            path_to_glue_job="simple_data_pipeline/task1.py",
        )
        GlueJob(
            datajob_stack=datajob_stack,
            glue_job_name="task2",
            path_to_glue_job="simple_data_pipeline/task2.py",
        )
        GlueJob(
            datajob_stack=datajob_stack,
            glue_job_name="task3",
            path_to_glue_job="simple_data_pipeline/task3.py",
        )
