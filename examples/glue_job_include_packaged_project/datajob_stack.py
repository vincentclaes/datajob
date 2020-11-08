from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob

with DataJobStack(
    stack_name="glue_job_include_packaged_project-job-include-packaged-project", stage="dev", project_root="./"
) as datajob_stack:
    datajob_stack.add(
        GlueJob(
            scope=datajob_stack,
            glue_job_name="task1",
            stage=datajob_stack.stage,
            path_to_glue_job="glue_job_include_packaged_project/task1.py",
        )
    )
