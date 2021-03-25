import unittest

from aws_cdk import core

from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob, GlueJobType


class TestGlueJob(unittest.TestCase):
    def setUp(self) -> None:
        self.app = core.App()

    def test_create_glue_pythonshell_successfully(self):
        djs = DataJobStack(scope=self.app, id="some-stack", stage="stg")
        glue_job = GlueJob(djs, "some-task", "some/path/task.py")
        self.assertEqual(glue_job.job_type, GlueJobType.PYTHONSHELL.value)
        self.assertEqual(glue_job.glue_version, "1.0")
        self.assertEqual(glue_job.job_path, "some/path/task.py")
        self.assertEqual(glue_job.python_version, "3")


if __name__ == "__main__":
    unittest.main()
