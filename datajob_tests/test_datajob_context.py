import unittest

from datajob.datajob_stack import DataJobStack, DataJobContext
from aws_cdk import core


class TestDatajobContext(unittest.TestCase):
    def test_datajob_context_initiates_without_error(self):
        exception_ = None
        try:
            app = core.App()
            djs = DataJobStack(scope=app, id="some-stack-name")
            DataJobContext(djs, unique_stack_name="some-unique-name")
        except Exception as e:
            exception_ = e
        self.assertIsNone(exception_)
