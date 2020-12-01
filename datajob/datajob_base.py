from aws_cdk import core

from datajob.datajob_stack import DataJobStack


class DataJobBase(core.Construct):

    def __init__(self, datajob_stack, glue_job_name, **kwargs):
        super().__init__(datajob_stack, glue_job_name, **kwargs)
        assert isinstance(datajob_stack, DataJobStack), f"we expect the scope argument to be of type {DataJobStack}"
        self.project_root = datajob_stack.project_root
        self.stage = datajob_stack.stage
        datajob_stack.resources.append(self)
