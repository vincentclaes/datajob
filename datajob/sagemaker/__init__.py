import stepfunctions.steps
from aws_cdk import aws_iam as iam

from datajob import logger
from datajob.datajob_base import DataJobBase
from datajob.datajob_stack import DataJobStack


def get_default_sagemaker_role(
    datajob_stack: DataJobStack, name: str = None
) -> iam.Role:
    name = name if name is not None else datajob_stack.unique_stack_name + "-sagemaker"
    return DataJobSagemakerBase.get_default_admin_role(
        datajob_stack, name, "sagemaker.amazonaws.com"
    )


class DataJobSagemakerBase(DataJobBase):
    def __init__(self, datajob_stack: DataJobStack, name: str, *args, **kwargs):
        super().__init__(datajob_stack, name)

    def create(self):
        logger.debug(
            "sagemaker does not implement the create "
            "function because it's not necessary/not supported to add these services to the datajob stack."
        )
