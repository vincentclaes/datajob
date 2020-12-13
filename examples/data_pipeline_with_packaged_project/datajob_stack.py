#!/usr/bin/env python

from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow
import pathlib

current_dir = pathlib.Path(__file__).parent.absolute()

with DataJobStack(
    stack_name="data-pipeline-pkg", project_root=current_dir
) as datajob_stack:
    task1 = GlueJob(
        datajob_stack=datajob_stack,
        name="task1",
        job_path="data_pipeline_with_packaged_project/task1.py",
    )

    task2 = GlueJob(
        datajob_stack=datajob_stack,
        name="task2",
        job_path="data_pipeline_with_packaged_project/task2.py",
    )

    with StepfunctionsWorkflow(
        datajob_stack=datajob_stack, name="data-pipeline-pkg"
    ) as sfn:
        task1 >> task2
