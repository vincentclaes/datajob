from abc import abstractmethod
from aws_cdk import core
from datajob.datajob_stack import DataJobStack
from datajob import logger

class DataJobBase(core.Construct):

    def __init__(self, datajob_stack, name, **kwargs):
        super().__init__(datajob_stack, name, **kwargs)
        assert isinstance(datajob_stack, DataJobStack), f"we expect the scope argument to be of type {DataJobStack}"
        self.name = name
        self.project_root = datajob_stack.project_root
        self.stage = datajob_stack.stage
        self.unique_name = f"{self.name}-{self.stage}"
        logger.info(f"adding job {self} to stack workflow resources")
        datajob_stack.resources.append(self)

    @abstractmethod
    def create(self):
        """create datajob"""