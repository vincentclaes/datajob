from datetime import datetime

from aws_cdk import aws_iam as iam
from stepfunctions.inputs import ExecutionInput

from datajob import logger
from datajob.datajob_base import DataJobBase


class DataJobSagemakerException(Exception):
    """"""


class DataJobSagemakerBase(DataJobBase):
    current_date = datetime.utcnow()
    MAX_CHARS = 63
    execution_input_schema = {}
    execution_input = None

    @staticmethod
    def generate_unique_name(
        name: str, max_chars: int = MAX_CHARS, datetime_format: str = "%Y%m%dT%H%M%S"
    ):
        current_date_as_string = DataJobSagemakerBase.current_date.strftime(
            datetime_format
        )
        total_length = len(current_date_as_string) + len(name)
        difference = max_chars - total_length
        if difference < 0:
            logger.debug(
                f"the length of the unique name is {total_length}. Max chars is {max_chars}. Removing last {difference} chars from name"
            )
            name = name[: difference - 1]
        unique_name = f"{name}-{current_date_as_string}"
        logger.debug(f"generated unique name is {unique_name}")
        return unique_name

    def handle_job_name(self, job_name):
        if job_name is None:
            logger.debug(
                f"job name not provided, we will return the unique name {self.unique_name}"
            )
            if self.unique_name in DataJobSagemakerBase.execution_input_schema:
                raise DataJobSagemakerException(
                    f"The entry {self.unique_name} already exists in the execution input."
                )
            DataJobSagemakerBase.execution_input_schema[self.unique_name] = str
            DataJobSagemakerBase.execution_input = ExecutionInput(
                schema=DataJobSagemakerBase.execution_input_schema
            )
            return DataJobSagemakerBase.execution_input[self.unique_name]
        else:
            return job_name

    def create(self):
        logger.debug(
            "sagemaker does not implement the create "
            "function because it's not necessary/not supported to add these services to the stack."
        )

    def get_default_role(self, name: str) -> iam.Role:
        name += "-sagemaker"
        return self._get_default_role(name, "sagemaker.amazonaws.com")
