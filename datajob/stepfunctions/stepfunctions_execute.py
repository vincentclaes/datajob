import time

from stepfunctions.workflow import Workflow, Execution

from datajob import logger


def _find_state_machine_arn(state_machine: str) -> str:
    """lookup the state machine arn based on the state machine name"""
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


def _get_status(execution: Execution):
    """get the status of a stepfunctions workflow execution."""
    time.sleep(1)
    description = execution.describe()
    return description.get("status")


def _execute(state_machine_arn: str):
    """execute statemachine based on the name."""
    workflow = Workflow.attach(state_machine_arn)
    return workflow.execute()
