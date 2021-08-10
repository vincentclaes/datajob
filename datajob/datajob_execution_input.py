import json
from typing import Union

from stepfunctions.inputs import ExecutionInput

from datajob import logger


class DataJobSagemakerException(Exception):
    ...


class DataJobExecutionInput(object):
    """singleton class that holds configuration on the execution input."""

    DATAJOB_EXECUTION_INPUT = "DatajobExecutionInput"

    def __init__(self):
        self.execution_input_schema = {}
        self.execution_input = None

    def add_execution_input(self, unique_name: str) -> None:
        logger.debug(f"adding execution input for {unique_name}")
        if unique_name in self.execution_input_schema:
            raise DataJobSagemakerException(
                f"The entry {unique_name} already exists in the execution input."
            )
        self.execution_input_schema[unique_name] = str
        self.execution_input = ExecutionInput(schema=self.execution_input_schema)

    def update_execution_input_for_stack(self, datajob_stack) -> None:
        """Add the keys of the execution input schema as a json string to the
        output variable `of the datajob stack.

        Args:
            datajob_stack: DataJob Stack instance

        Returns: None
        """
        execution_input_schema_keys = json.dumps(
            list(self.execution_input_schema.keys())
        )
        datajob_stack.update_datajob_stack_outputs(
            key=self.DATAJOB_EXECUTION_INPUT,
            value=execution_input_schema_keys,
        )

    def handle_argument_for_execution_input(
        self, datajob_stack, argument, unique_name
    ) -> Union[str, ExecutionInput]:
        """If the user provided an argument we will return it as is. If the
        argument is None, hence not provided by the user, we will add it as a
        stepfunctions.ExecutionInput.

        more info here: https://aws-step-functions-data-science-sdk.readthedocs.io/en/stable/placeholders.html

        Args:
            datajob_stack: DataJob Stack instance
            argument: an argument passed to the sagemaker task by the user.

        Returns: the argument value or the execution input.
        """
        if argument is not None:
            logger.debug(
                f"parameter value {argument} is not None, we are just returning the value."
            )
            return argument
        logger.debug(f"no argument provided, we will construct an execution input.")
        self.add_execution_input(unique_name)
        self.update_execution_input_for_stack(datajob_stack=datajob_stack)
        return self.execution_input[unique_name]
