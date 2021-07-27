import json
import time
from typing import Union

import boto3
from stepfunctions.workflow import Execution
from stepfunctions.workflow import Workflow

from datajob import console
from datajob import logger
from datajob.sagemaker.sagemaker_job import DataJobSagemakerBase


def _find_state_machine_arn(state_machine: str) -> str:
    """lookup the state machine arn based on the state machine name."""
    workflows = Workflow.list_workflows()
    state_machine_object = [
        workflow for workflow in workflows if workflow.get("name") == state_machine
    ]
    if len(state_machine_object) == 1:
        logger.debug(f"we have found one statemachine {state_machine_object[0]}")
        return state_machine_object[0].get("stateMachineArn")
    elif len(state_machine_object) == 0:
        logger.error(f"statemachine {state_machine} not found.")
        raise LookupError("no statemachine found.")
    else:
        logger.error(f"more than one statemachine found with name {state_machine}.")
        raise Exception(
            "more than one statemachine found. Something strange is going on ..."
        )


def _describe_stack_resources(sfn_arn: str) -> dict:
    """Describe stack resources for a stepfunctions workflow arn."""
    return boto3.client("cloudformation").describe_stack_resources(
        PhysicalResourceId=sfn_arn
    )


def _find_cloudformation_stack_name_for_sfn_workflow(sfn_arn: str) -> str:
    """Find the cloudformation stackname for a stepfunction workflow.

    Args:
        sfn_arn: the AWS ARN of stepfunctions workflow

    Returns: Stackname
    """
    logger.debug(f"looking for the stack for step functions arn {sfn_arn}")
    stack_resources = _describe_stack_resources(sfn_arn=sfn_arn)
    stepfunctions_resource = [
        element
        for element in stack_resources.get("StackResources")
        if element.get("PhysicalResourceId") == sfn_arn
    ]
    stack_name = stepfunctions_resource[0]["StackName"]
    logger.debug(f"found stack {stack_name}")
    return stack_name


def _describe_stacks(stack_name: str) -> dict:
    return boto3.client("cloudformation").describe_stacks(StackName=stack_name)


def _get_execution_input_from_stack(stack_name: str) -> Union[dict, None]:
    """Look for the execution input in the outputs of this stack. If present
    generate unique names for the ExecutionInput and return the dict. If not
    present return None.

    Args:
        stack_name: name of the cloudformation stack.

    Returns: ExecutionInput as a dict or None
    """
    logger.debug(f"looking for execution input in {stack_name}")
    stack = _describe_stacks(stack_name=stack_name)
    outputs = stack.get("Stacks")[0].get("Outputs")
    if outputs:
        for output in outputs:
            if output.get("OutputKey") == DataJobSagemakerBase.DATAJOB_EXECUTION_INPUT:
                execution_inputs = json.loads(output.get("OutputValue"))

                return_value = {
                    execution_input: DataJobSagemakerBase.generate_unique_name(
                        execution_input
                    )
                    for execution_input in execution_inputs
                }

                console.log("execution input found: \n" f"{return_value}")
                return return_value
    logger.debug("no execution input found.")


def get_execution_input(sfn_arn: str) -> Union[dict, None]:
    """Get execution input dict for a workflow.

    - we will first find the cloudformation stack name based on the stepfunctions workflow arn.
    - then we try to get the execution input schema from the cloudformation stack "Outputs".

    Args:
        sfn_arn: arn of the stepfunctions workflow

    Returns: ExecutionInput or None
    """
    stack_name = _find_cloudformation_stack_name_for_sfn_workflow(sfn_arn=sfn_arn)
    return _get_execution_input_from_stack(stack_name=stack_name)


def _get_status(execution: Execution):
    """get the status of a stepfunctions workflow execution."""
    time.sleep(1)
    description = execution.describe()
    return description.get("status")


def _execute(state_machine_arn: str, execution_input: Union[dict, None]):
    """execute statemachine based on the name."""
    workflow = Workflow.attach(state_machine_arn)
    return workflow.execute(inputs=execution_input)
