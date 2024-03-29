import pathlib
import unittest
from unittest.mock import patch

from typer.testing import CliRunner

from datajob import datajob

current_dir = str(pathlib.Path(__file__).absolute().parent)


class TestDatajobDeploy(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = CliRunner()

    @patch("datajob.datajob.call_cdk")
    def test_datajob_deploy_cli_runs_successfully(self, m_call_cdk):
        result = self.runner.invoke(
            datajob.app,
            ["deploy", "--config", "some_config.py", "--stage", "some-stage"],
        )
        self.assertEqual(result.exit_code, 0)

    @patch("datajob.datajob.call_cdk")
    def test_datajob_deploy_cli_runs_with_unknown_args_successfully(self, m_call_cdk):
        result = self.runner.invoke(
            datajob.app,
            [
                "deploy",
                "--config",
                "some_config.py",
                "--stage",
                "some-stage",
                "--unknown-arg",
                "unkown-value",
            ],
        )
        self.assertEqual(result.exit_code, 0)

    @patch("datajob.package.wheel.create_wheel")
    @patch("datajob.datajob.call_cdk")
    def test_datajob_deploy_cli_runs_with_project_root_successfully(
        self, m_call_cdk, m_create_wheel
    ):
        result = self.runner.invoke(
            datajob.app,
            [
                "deploy",
                "--config",
                "some_config.py",
                "--stage",
                "some-stage",
                "--package",
                "poetry",
            ],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(m_create_wheel.call_count, 1)

    @patch("datajob.package.wheel._poetry_wheel")
    @patch("datajob.datajob.call_cdk")
    def test_datajob_deploy_with_package_poetry(self, m_call_cdk, m_create_wheel):
        result = self.runner.invoke(
            datajob.app,
            [
                "deploy",
                "--config",
                "some_config.py",
                "--stage",
                "some-stage",
                "--package",
                "poetry",
            ],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(m_create_wheel.call_count, 1)

    @patch("datajob.package.wheel._setuppy_wheel")
    @patch("datajob.datajob.call_cdk")
    def test_datajob_deploy_with_package_setuppy(self, m_call_cdk, m_create_wheel):
        result = self.runner.invoke(
            datajob.app,
            [
                "deploy",
                "--config",
                "some_config.py",
                "--stage",
                "some-stage",
                "--package",
                "setuppy",
            ],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(m_create_wheel.call_count, 1)

    @patch("datajob.datajob.call_cdk")
    def test_datajob_deploy_cli_runs_with_stage_successfully(self, m_call_cdk):
        result = self.runner.invoke(
            datajob.app,
            ["deploy", "--config", "some_config.py", "--stage", "some-stage"],
        )
        self.assertEqual(result.exit_code, 0)

    @patch("datajob.datajob.call_cdk")
    def test_datajob_deploy_cli_runs_with_no_stage_successfully(self, m_call_cdk):
        result = self.runner.invoke(
            datajob.app, ["deploy", "--config", "some_config.py"]
        )
        self.assertEqual(result.exit_code, 0)
