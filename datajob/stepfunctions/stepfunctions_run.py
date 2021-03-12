import boto3
from stepfunctions.workflow import Workflow


def _get_cloudformation_resource(stack_name: str, next_token=None) -> dict:
    if next_token:
        return boto3.client("cloudformation").list_stack_resources(
            StackName=stack_name, NextToken=next_token
        )
    return boto3.client("cloudformation").list_stack_resources(StackName=stack_name)


def _get_all_cloudformation_resources(stack_name: str, next_token: str = None):
    stack_resources = _get_cloudformation_resource(
        stack_name=stack_name, next_token=next_token
    )
    stack_resource_summary = stack_resources.get("StackResourceSummaries")
    next_token = stack_resources.get("NextToken")
    if next_token is not None:
        stack_resource_summary += _get_all_cloudformation_resources(
            stack_name=stack_name, next_token=next_token
        )
    return stack_resource_summary


def run(stack_name: str) -> None:
    resources = _get_all_cloudformation_resources(stack_name)
    sfn_statemachines = [
        resource
        for resource in resources
        if resource.get("ResourceType") == "AWS::StepFunctions::StateMachine"
    ]
    if len(sfn_statemachines) == 0:
        raise LookupError("no stepfunctions statemachines found in the stack.")
    assert (
        len(sfn_statemachines) == 1
    ), "We only support 1 stepfunction per stack at the moment"
    workflow = Workflow.attach(sfn_statemachines.get("PhysicalResourceId"))
    workflow.execute()
