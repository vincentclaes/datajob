import unittest

from datajob.datajob_stack import DataJobStack
from aws_cdk import core


class TestDatajobStack(unittest.TestCase):
    def test_datajob_stack_initiates_without_error(self):
        exception_ = None
        try:
            with DataJobStack(stack_name="datajob-stack-no-error") as djs:
                pass
        except Exception as e:
            exception_ = e
        self.assertIsNone(exception_)

    def test_datajob_stack_with_no_stage(self):
        with DataJobStack(stack_name="datajob-stack-no-stage") as djs:
            pass
        self.assertEqual(djs.stage, DataJobStack.STAGE_VALUE_DEFAULT)

    def test_datajob_stack_with_stage_passed_via_cli(self):
        stage_value = "some-value"
        scope = core.App(context={"stage": stage_value})
        with DataJobStack(stack_name="datajob-stack-no-error", scope=scope) as djs:
            pass
        self.assertEqual(djs.stage, stage_value)

    def test_datajob_stack_with_stage_passed_to_datajob_stack(self):
        stage_value = "some-value"
        with DataJobStack(
            stack_name="datajob-stack-no-error", stage=stage_value
        ) as djs:
            pass
        self.assertEqual(djs.stage, stage_value)
