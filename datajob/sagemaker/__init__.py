import json
from datetime import datetime
from typing import Union

from aws_cdk import aws_iam as iam
from stepfunctions.inputs import ExecutionInput

from datajob import logger
from datajob.datajob_base import DataJobBase
from datajob.datajob_stack import DataJobStack


class DataJobSagemakerException(Exception):
    """"""


class DataJobSagemakerBase(DataJobBase):
    DATAJOB_EXECUTION_INPUT = "DatajobExecutionInput"
    current_date = datetime.utcnow()
    MAX_CHARS = 63
    execution_input_schema = {}
    execution_input = None

    def __init__(self, datajob_stack: DataJobStack, name: str, *args, **kwargs):
        super().__init__(datajob_stack, name)

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

    def handle_argument_for_execution_input(
        self, datajob_stack, argument
    ) -> Union[str, ExecutionInput]:
        """if the argument is None, hence not provided by the user, we will
        create a unique name and apply a stepfunctions ExecutionInput.

        Args:
            datajob_stack: DataJob Stack instance
            argument: an argument passed to the sagemaker task by the user.

        Returns: the argument value or
        """
        if argument is not None:
            logger.debug(
                f"parameter value {argument} is not None, we are just returning the value."
            )
            return argument
        logger.debug(f"job name not provided, we will construct an execution input.")
        if self.unique_name in DataJobSagemakerBase.execution_input_schema:
            raise DataJobSagemakerException(
                f"The entry {self.unique_name} already exists in the execution input."
            )
        DataJobSagemakerBase.execution_input_schema[self.unique_name] = str
        DataJobSagemakerBase.execution_input = ExecutionInput(
            schema=DataJobSagemakerBase.execution_input_schema
        )
        self._update_execution_input_for_stack(datajob_stack=datajob_stack)
        return DataJobSagemakerBase.execution_input[self.unique_name]

    @staticmethod
    def _update_execution_input_for_stack(datajob_stack: DataJobStack) -> None:
        """Add the keys of the execution input schema as a json string to the
        output variable `of the datajob stack.

        Args:
            datajob_stack: DataJob Stack instance

        Returns: None
        """
        execution_input_schema_keys = json.dumps(
            list(DataJobSagemakerBase.execution_input_schema.keys())
        )
        datajob_stack.update_datajob_stack_outputs(
            key=DataJobSagemakerBase.DATAJOB_EXECUTION_INPUT,
            value=execution_input_schema_keys,
        )

    def create(self):
        logger.debug(
            "sagemaker does not implement the create "
            "function because it's not necessary/not supported to add these services to the stack."
        )

    def get_default_role(self, name: str) -> iam.Role:
        name += "-sagemaker"
        return self._get_default_role(name, "sagemaker.amazonaws.com")
