import unittest

from aws_cdk import core

from datajob.datajob_stack import DataJobContext
from datajob.datajob_stack import DataJobStack


class TestDataJobContext(unittest.TestCase):
    def test_datajob_context_initiates_without_stage(self):
        exception_ = None
        try:
            app = core.App()
            djs = DataJobStack(scope=app, id="some-stack-name")
            djc = DataJobContext(djs)
        except Exception as e:
            exception_ = e
        self.assertIsNone(exception_)
        # some random characters are appended to the bucketname
        self.assertIsNone(djc.stage)
        self.assertTrue(len(djc.data_bucket_name.split("-")[-1]), 4)
        self.assertTrue(len(djc.deployment_bucket_name.split("-")[-1]), 4)

    def test_datajob_context_with_stage(self):
        exception_ = None
        try:
            stack_name = "some-stack"
            stage = "some-stage"
            app = core.App()
            djs = DataJobStack(scope=app, id=stack_name, stage=stage)
            djc = DataJobContext(djs)
            self.assertIsNotNone(djc.stage)
            self.assertEqual(djc.data_bucket_name, djs.unique_stack_name)
            self.assertTrue(
                djc.deployment_bucket_name, f"{djs.unique_stack_name}-deployment-bucket"
            )
        except Exception as e:
            exception_ = e
        self.assertIsNone(exception_)
