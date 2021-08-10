import unittest

from aws_cdk import core
from stepfunctions.steps import Task

from datajob.datajob_base import DataJobBase
from datajob.datajob_stack import DataJobStack


class TestDataJobBase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = core.App()
        self.djs = DataJobStack(scope=self.app, id="datajob-stack-no-error")

    def test_datajob_base_subclass_does_not_implements_sfn_task(self):
        class SomeTaskWithoutSfnTask(DataJobBase):
            def create(self):
                pass

        without_sfn_task = SomeTaskWithoutSfnTask(
            datajob_stack=self.djs, name="without-sfn-task"
        )
        with self.assertRaises(NotImplementedError):
            without_sfn_task.sfn_task

    def test_datajob_base_subclass_implements_sfn_task(self):
        class SomeTaskWithSfnTask(DataJobBase):
            def __init__(self, datajob_stack, name):
                super().__init__(datajob_stack, name)
                self.sfn_task = Task(state_id="some-id")

            def create(self):
                pass

        with_sfn_task = SomeTaskWithSfnTask(
            datajob_stack=self.djs, name="without-sfn-task"
        )
        exception_ = None
        try:
            with_sfn_task.sfn_task
        except Exception as e:
            exception_ = e
        self.assertIsNone(exception_)
