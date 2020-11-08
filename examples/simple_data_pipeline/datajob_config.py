from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
with DataJobStack(stack_name="simple-data-pipeline", stage="dev") as datajob_stack:
    datajob_stack.add(
        GlueJob(
            datajob_stack,
            stage=datajob_stack.stage,
            path_to_glue_job="glue/task1.py",
            job_type="pythonshell",
            glue_version="1.0",
            python_version="3",
        )
    )