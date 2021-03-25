import os
import unittest

from aws_cdk import core
from moto import mock_stepfunctions
from stepfunctions.steps.compute import GlueStartJobRunStep
from stepfunctions.steps.states import Parallel

from datajob.datajob_stack import DataJobStack
from datajob.stepfunctions import stepfunctions_workflow
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow


@stepfunctions_workflow.task
class SomeMockedClass(object):
    def __init__(self, unique_name):
        self.unique_name = unique_name


class TestStepfunctionsWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # we need a AWS region else these tests will fail with boto3 stepfunctions.
        # (even when using moto to mock stepfunctions!)
        try:
            os.environ["AWS_DEFAULT_REGION"]
        except KeyError:
            os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"

    def setUp(self) -> None:
        self.app = core.App()

    @mock_stepfunctions
    def test_create_tasks_for_orchestration_simple_flow_successfully(self):
        task1 = stepfunctions_workflow.task(SomeMockedClass("task1"))
        task2 = stepfunctions_workflow.task(SomeMockedClass("task2"))
        task3 = stepfunctions_workflow.task(SomeMockedClass("task3"))
        task4 = stepfunctions_workflow.task(SomeMockedClass("task4"))
        djs = DataJobStack(
            scope=self.app,
            id="a-unique-name-1",
            stage="stage",
            project_root="sampleproject/",
            region="eu-west-1",
            account="3098726354",
        )
        with StepfunctionsWorkflow(djs, "some-name") as a_step_functions_workflow:
            task1 >> [task2, task3] >> task4

        self.assertTrue(
            isinstance(a_step_functions_workflow.chain_of_tasks[0], GlueStartJobRunStep)
        )
        self.assertTrue(
            isinstance(a_step_functions_workflow.chain_of_tasks[1], Parallel)
        )
        self.assertTrue(
            isinstance(a_step_functions_workflow.chain_of_tasks[2], GlueStartJobRunStep)
        )

    @mock_stepfunctions
    def test_create_tasks_for_orchestration_starts_with_parallel_flow_successfully(
        self,
    ):
        task1 = stepfunctions_workflow.task(SomeMockedClass("task1"))
        task2 = stepfunctions_workflow.task(SomeMockedClass("task2"))
        task3 = stepfunctions_workflow.task(SomeMockedClass("task2"))
        djs = DataJobStack(
            scope=self.app,
            id="a-unique-name-2",
            stage="stage",
            project_root="sampleproject/",
            region="eu-west-1",
            account="3098726354",
        )
        with StepfunctionsWorkflow(djs, "some-name") as a_step_functions_workflow:
            [task1, task2] >> task3

        self.assertTrue(
            isinstance(a_step_functions_workflow.chain_of_tasks[0], Parallel)
        )
        self.assertTrue(
            isinstance(a_step_functions_workflow.chain_of_tasks[1], GlueStartJobRunStep)
        )
