import unittest

from aws_cdk import core

from datajob.datajob_stack import DataJobStack


class TestDataJobStack(unittest.TestCase):
    def setUp(self) -> None:
        self.app = core.App()

    def test_datajob_stack_initiates_without_error(self):
        exception_ = None
        try:
            with DataJobStack(scope=self.app, id="datajob-stack-no-error") as djs:
                pass
        except Exception as e:
            exception_ = e
        self.assertIsNone(exception_)

    def test_datajob_stack_with_no_stage(self):
        with DataJobStack(scope=self.app, id="datajob-stack-no-stage") as djs:
            pass
        self.assertIsNone(djs.stage)

    def test_datajob_stack_with_stage_passed_via_cli(self):
        stage_value = "some-value"
        scope = core.App(context={"stage": stage_value})
        with DataJobStack(scope=scope, id="datajob-stack-no-error") as djs:
            pass
        self.assertEqual(djs.stage, stage_value)

    def test_datajob_stack_with_stage_passed_to_datajob_stack(self):
        stage_value = "some-value"
        with DataJobStack(
            scope=self.app, id="datajob-stack-no-error", stage=stage_value
        ) as djs:
            pass
        self.assertEqual(djs.stage, stage_value)
