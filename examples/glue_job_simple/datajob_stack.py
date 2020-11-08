from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob

with DataJobStack(stack_name="simple-data-pipeline", stage="dev") as datajob_stack:
    datajob_stack.add(
        GlueJob(
            scope=datajob_stack,
            glue_job_name="task1",
            stage=datajob_stack.stage,
            path_to_glue_job="glue/task1.py",
        )
    )
