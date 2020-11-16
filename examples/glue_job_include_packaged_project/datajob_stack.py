from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
import pathlib

current_dir = pathlib.Path(__file__).parent.absolute()

with DataJobStack(
    stack_name="some-glue-job", stage="dev", project_root=current_dir
) as datajob_stack:
    datajob_stack.add(
        GlueJob(
            scope=datajob_stack,
            glue_job_name="task1",
            stage=datajob_stack.stage,
            path_to_glue_job="glue_job_include_packaged_project/task1.py",
            project_root=datajob_stack.project_root
        )
    )
