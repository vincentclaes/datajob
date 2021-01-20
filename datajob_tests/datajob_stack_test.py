import unittest
from datajob.datajob_stack import DataJobStack


class DatajobStackTest(unittest.TestCase):
    def test_datajob_stack_initiates_without_error(self):
        exception_ = None
        try:
            with DataJobStack(stack_name="some-stack-name") as djs:
                pass
        except Exception as e:
            exception_ = e
        self.assertIsNone(exception_)

    def test_datajob_stack_with_no_stage(self):
        with DataJobStack(stack_name="some-stack-name") as djs:
            pass
        self.assertEqual(djs.stage, DataJobStack.DEFAULT_STAGE)
