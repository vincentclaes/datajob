import io
import json
import os
import unittest

import yaml
from aws_cdk import core
from moto import mock_stepfunctions
from stepfunctions.steps.states import Parallel
from stepfunctions.steps.states import Task

from datajob.datajob_stack import DataJobStack
from datajob.stepfunctions import stepfunctions_workflow
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow


@stepfunctions_workflow.task
class SomeMockedClass(Task):
    def __init__(self, unique_name, *args, **kwargs):
        super(SomeMockedClass, self).__init__(state_id=unique_name, *args, **kwargs)
        self.unique_name = unique_name

    def accept(self, visitor):
        pass


class TestStepfunctions(unittest.TestCase):
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
        task5 = stepfunctions_workflow.task(SomeMockedClass("task5"))

        djs = DataJobStack(
            scope=self.app,
            id="a-unique-name-1",
            stage="stage",
            project_root="sampleproject/",
            region="eu-west-1",
            account="3098726354",
        )
        with StepfunctionsWorkflow(djs, "some-name") as a_step_functions_workflow:
            task1 >> task2 >> task4
            task3 >> task2
            task5 >> task2

        parallel_branch = a_step_functions_workflow.chain_of_tasks.steps[0]
        self.assertEqual(parallel_branch.state_type, "Parallel")
        self.assertEqual(len(parallel_branch.branches), 3)

        self.assertEqual(
            a_step_functions_workflow.chain_of_tasks.steps[1].state_type, "Task"
        )
        self.assertEqual(
            a_step_functions_workflow.chain_of_tasks.steps[1].state_id, "task2"
        )
        self.assertEqual(
            a_step_functions_workflow.chain_of_tasks.steps[2].state_type, "Task"
        )
        self.assertEqual(
            a_step_functions_workflow.chain_of_tasks.steps[2].state_id, "task4"
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
            task1 >> task3
            task2 >> task3

        self.assertTrue(
            isinstance(a_step_functions_workflow.chain_of_tasks.steps[0], Parallel)
        )
        self.assertTrue(
            isinstance(
                a_step_functions_workflow.chain_of_tasks.steps[1], SomeMockedClass
            )
        )

    @mock_stepfunctions
    def test_orchestrate_1_task_successfully(
        self,
    ):
        task1 = stepfunctions_workflow.task(SomeMockedClass("task1"))
        djs = DataJobStack(
            scope=self.app,
            id="a-unique-name-2",
            stage="stage",
            project_root="sampleproject/",
            region="eu-west-1",
            account="3098726354",
        )
        with StepfunctionsWorkflow(djs, "some-name") as a_step_functions_workflow:
            task1 >> ...

        self.assertTrue(
            isinstance(
                a_step_functions_workflow.chain_of_tasks.steps[0], SomeMockedClass
            )
        )

    @mock_stepfunctions
    def test_create_workflow_with_notification_successfully(self):
        task1 = stepfunctions_workflow.task(SomeMockedClass("task1"))
        task2 = stepfunctions_workflow.task(SomeMockedClass("task2"))

        djs = DataJobStack(
            scope=self.app,
            id="a-unique-name-3",
            stage="stage",
            project_root="sampleproject/",
            region="eu-west-1",
            account="3098726354",
        )
        with StepfunctionsWorkflow(
            djs, "some-name", notification="email@domain.com"
        ) as a_step_functions_workflow:
            task1 >> task2

        with io.StringIO() as f:
            f.write(a_step_functions_workflow.workflow.get_cloudformation_template())
            f.seek(0)
            cf_template = yaml.load(f, Loader=yaml.FullLoader)

        sfn_workflow = json.loads(
            cf_template.get("Resources")
            .get("StateMachineComponent")
            .get("Properties")
            .get("DefinitionString")
        )
        # we expect two notifications; 1 for success and one for failure
        self.assertTrue("SuccessNotification" in sfn_workflow.get("States").keys())
        self.assertTrue("FailureNotification" in sfn_workflow.get("States").keys())
        # there is a catch statement in the statemachine
        self.assertTrue(
            "Catch" in sfn_workflow.get("States").get("notification").keys()
        )
        # when implementing a notification we expect a Parallel branch
        self.assertEqual(
            sfn_workflow.get("States").get("notification").get("Type"), "Parallel"
        )
