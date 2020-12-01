from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob

with DataJobStack(stack_name="simple-data-pipeline", stage="dev") as datajob_stack:
        GlueJob(
            datajob_stack=datajob_stack,
            glue_job_name="task1",
            path_to_glue_job="glue_job_simple/task1.py",
        )
