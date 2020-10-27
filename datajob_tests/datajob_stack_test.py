import unittest

from aws_cdk import core
from moto import mock_s3

from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob


class DataJobStackTest(unittest.TestCase):
    @mock_s3
    def test_datajob_stack_runs_without_errors_successfully(self):
        with DataJobStack(
            scope=core.App(),
            unique_stack_name="a-unique-name",
            stage="stage",
            project_root="/Users/vincent/Workspace/datajob/datajob_tests/sampleproject",
            env={"region": "eu-west-1", "account": "3098726354"},
        ) as djs:

            djs.add(
                GlueJob(
                    djs,
                    "test",
                    stage=djs.stage,
                    path_to_glue_job="sampleproject/src/sample/simple.py",
                    job_type="pythonshell",
                    glue_version="1.0",
                    max_capacity=1,
                    python_version="3",
                    arguments={
                        "--some-args": f"some-value",
                    },
                )
            )


if __name__ == "__main__":
    unittest.main()
