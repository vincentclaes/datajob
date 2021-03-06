import datetime
import pathlib
import unittest
from unittest.mock import patch, MagicMock, Mock

from stepfunctions.workflow import Workflow, Execution, ExecutionStatus

from typer.testing import CliRunner

from datajob import datajob
from datajob.stepfunctions import stepfunctions_execute

current_dir = str(pathlib.Path(__file__).absolute().parent)


class TestDatajobExecute(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = CliRunner()

    def get_execution(
        self,
        status=ExecutionStatus.Running,
        arn="arn:aws:states:eu-west-1:123456789012:stateMachine:some-state-machine",
    ) -> Execution:
        execution = Mock(spec=Execution, execution_arn=arn)
        attrs = {"describe.return_value": {"status": status}}
        execution.configure_mock(**attrs)
        return execution

    @patch("datajob.stepfunctions.stepfunctions_execute._execute")
    @patch.object(Workflow, "list_workflows")
    def test_datajob_cli_run_with_no_errors(self, m_list_workflow, m_execute):
        some_state_machine = "some-statemachine-1"
        some_state_machine_arn = (
            f"arn:aws:states:eu-west-1:123456789012:stateMachine:{some_state_machine}"
        )
        execution = self.get_execution()
        m_execute.return_value = execution

        m_list_workflow.return_value = [
            {
                "stateMachineArn": f"{some_state_machine_arn}",
                "name": f"{some_state_machine}",
                "type": "STANDARD",
                "creationDate": datetime.datetime(2020, 11, 12, 22, 9, 26, 5000),
            },
            {
                "stateMachineArn": "arn:aws:states:eu-west-1:303915887987:stateMachine:some-statemachine-2",
                "name": "some-statemachine-2",
                "type": "STANDARD",
                "creationDate": datetime.datetime(2020, 11, 12, 22, 9, 26, 5000),
            },
            {
                "stateMachineArn": "arn:aws:states:eu-west-1:303915887987:stateMachine:some-statemachine-3",
                "name": "some-statemachine-3",
                "type": "STANDARD",
                "creationDate": datetime.datetime(2020, 11, 12, 22, 9, 26, 5000),
            },
        ]

        result = self.runner.invoke(
            datajob.app, ["execute", "--state-machine", some_state_machine]
        )

        self.assertEqual(result.exit_code, 0)
