import unittest

from moto import mock_s3

from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob


class DataJobStackTest(unittest.TestCase):
    @mock_s3
    def test_datajob_stack_runs_without_errors(self):
        self.exception_ = None
        try:
            with DataJobStack(
                stack_name="a-unique-name",
                stage="stage",
                project_root="sampleproject/",
                region="eu-west-1",
                account="3098726354",
            ) as djs:
                GlueJob(
                    djs,
                    "test",
                    path_to_glue_job="src/sample/simple.py",
                    job_type="pythonshell",
                    glue_version="1.0",
                    max_capacity=1,
                    python_version="3",
                    arguments={
                        "--some-args": f"some-value",
                    },
                )
        except Exception as e:
            self.exception_ = e
        finally:
            self.assertIsNone(self.exception_)


if __name__ == "__main__":
    unittest.main()
