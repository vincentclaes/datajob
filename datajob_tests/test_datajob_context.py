import unittest

from datajob.datajob_stack import DataJobStack, DatajobContext


class TestDatajobContext(unittest.TestCase):
    def test_datajob_context_initiates_without_error(self):
        exception_ = None
        try:
            djs = DataJobStack(stack_name="some-stack-name")
            DatajobContext(djs, unique_stack_name="some-unique-name")
        except Exception as e:
            exception_ = e
        self.assertIsNone(exception_)
