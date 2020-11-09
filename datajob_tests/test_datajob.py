import unittest
from datajob import datajob
from sys import argv
from mock import patch
import typer
from typer.testing import CliRunner


class DatajobTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = CliRunner()

    @patch("datajob.datajob.call_cdk")
    def test_datajob_deploy_cli_runs_successfully(self, m_call_cdk):
        result = self.runner.invoke(
            datajob.app, ["deploy", "--config", "some_config.py"]
        )
        self.assertEqual(result.exit_code, 0)

    @patch("datajob.datajob.call_cdk")
    def test_datajob_deploy_cli_runs_with_unknown_args_successfully(self, m_call_cdk):
        result = self.runner.invoke(
            datajob.app,
            ["deploy", "--config", "some_config.py", "--unknown-arg", "unkown-value"],
        )
        self.assertEqual(result.exit_code, 0)

    @patch("datajob.package.wheel.create")
    @patch("datajob.datajob.call_cdk")
    def test_datajob_deploy_cli_runs_with_project_root_successfully(self, m_call_cdk, m_create_wheel):
        result = self.runner.invoke(
            datajob.app,
            ["deploy", "--config", "some_config.py", "--package"],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(m_create_wheel.call_count, 1)


if __name__ == "__main__":
    unittest.main()
