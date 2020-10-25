import unittest
from aws_cdk import core
from datajob.datajob_stack import DataJobStack
from datajob import ROOT_DIR
from moto import mock_s3
from datajob.data_job_context import DataJobContext

from datajob.glue.glue_job import GlueJob
from mock import patch

class DataJobStackTest(unittest.TestCase):

    @mock_s3
    # @patch.object(DataJobContext, "_create_wheel_for_glue_job")
    # def test_datajob_stack_runs_without_errors_successfully(self, m_create_whl):
    def test_datajob_stack_runs_without_errors_successfully(self):
        with DataJobStack(scope=core.App(),
                     unique_stack_name="a-unique-name",
                     stage="stage",
                     project_root="/Users/vincent/Workspace/datajob/datajob_tests/sampleproject",
                     env={"region": "eu-west-1", "account": "3098726354"}
                     ) as djs:
            GlueJob()



if __name__ == '__main__':
    unittest.main()
