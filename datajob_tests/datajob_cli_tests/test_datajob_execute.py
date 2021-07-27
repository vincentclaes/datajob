import datetime
import pathlib
import unittest
from unittest.mock import Mock
from unittest.mock import patch

from stepfunctions.workflow import Execution
from stepfunctions.workflow import ExecutionStatus
from stepfunctions.workflow import Workflow
from typer.testing import CliRunner

from datajob import datajob

current_dir = str(pathlib.Path(__file__).absolute().parent)


class TestDatajobExecute(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = CliRunner()

    @patch("datajob.stepfunctions.stepfunctions_execute._describe_stacks")
    @patch("datajob.stepfunctions.stepfunctions_execute._describe_stack_resources")
    @patch("datajob.stepfunctions.stepfunctions_execute.execute")
    @patch.object(Workflow, "list_workflows")
    def test_datajob_cli_execute_with_no_errors(
        self, m_list_workflow, m_execute, m_describe_resources, m_describe_stack
    ):
        some_state_machine = "some-statemachine-1"
        some_state_machine_arn = (
            f"arn:aws:states:eu-west-1:123456789012:stateMachine:{some_state_machine}"
        )
        execution = self.get_execution()
        m_execute.return_value = execution
        stack_resources = self.describe_stack_resources(
            some_state_machine_arn=some_state_machine_arn
        )
        m_describe_resources.return_value = stack_resources
        stack = self.describe_stack()
        m_describe_stack.return_value = stack
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

    def get_execution(
        self,
        status=ExecutionStatus.Running,
        arn="arn:aws:states:eu-west-1:123456789012:stateMachine:some-state-machine",
    ) -> Execution:
        execution = Mock(spec=Execution, execution_arn=arn)
        attrs = {"describe.return_value": {"status": status}}
        execution.configure_mock(**attrs)
        return execution

    def describe_stack_resources(self, some_state_machine_arn):
        """mock of the return value of datajob.stepfunctions.stepfunctions_exec
        ute._describe_stack_resources."""
        return {
            "StackResources": [
                {
                    "StackName": "datajob-ml-pipeline-scikitlearn",
                    "StackId": "arn:aws:cloudformation:eu-west-1:077590795309:stack/datajob-ml-pipeline-scikitlearn/92c281d0-ead0-11eb-b822-028def2227ad",
                    "LogicalResourceId": "CDKMetadata",
                    "PhysicalResourceId": "92c281d0-ead0-11eb-b822-028def2227ad",
                    "ResourceType": "AWS::CDK::Metadata",
                    "Timestamp": datetime.datetime(2021, 7, 22, 12, 41, 17, 59000),
                    "ResourceStatus": "UPDATE_COMPLETE",
                    "DriftInformation": {"StackResourceDriftStatus": "NOT_CHECKED"},
                },
                {
                    "StackName": "datajob-ml-pipeline-scikitlearn",
                    "StackId": "arn:aws:cloudformation:eu-west-1:077590795309:stack/datajob-ml-pipeline-scikitlearn/92c281d0-ead0-11eb-b822-028def2227ad",
                    "LogicalResourceId": "datajobmlpipelinescikitlearndatajobmlpipelinescikitlearn8b89deploymentbucket2A30B920",
                    "PhysicalResourceId": "datajob-ml-pipeline-scikitlearn-8b89-deployment-bucket",
                    "ResourceType": "AWS::S3::Bucket",
                    "Timestamp": datetime.datetime(2021, 7, 23, 12, 29, 27, 662000),
                    "ResourceStatus": "CREATE_COMPLETE",
                    "DriftInformation": {"StackResourceDriftStatus": "NOT_CHECKED"},
                },
                {
                    "StackName": "datajob-ml-pipeline-scikitlearn",
                    "StackId": "arn:aws:cloudformation:eu-west-1:077590795309:stack/datajob-ml-pipeline-scikitlearn/92c281d0-ead0-11eb-b822-028def2227ad",
                    "LogicalResourceId": "datajobmlpipelinescikitlearnworkflow",
                    "PhysicalResourceId": some_state_machine_arn,
                    "ResourceType": "AWS::StepFunctions::StateMachine",
                    "Timestamp": datetime.datetime(2021, 7, 23, 12, 29, 8, 956000),
                    "ResourceStatus": "UPDATE_COMPLETE",
                    "DriftInformation": {"StackResourceDriftStatus": "NOT_CHECKED"},
                },
            ]
        }

    def describe_stack(self):
        """mock a description of a stack."""
        return {
            "Stacks": [
                {
                    "StackId": "arn:aws:cloudformation:eu-west-1:077590795309:stack/datajob-ml-pipeline-scikitlearn/92c281d0-ead0-11eb-b822-028def2227ad",
                    "StackName": "datajob-ml-pipeline-scikitlearn",
                    "ChangeSetId": "arn:aws:cloudformation:eu-west-1:077590795309:changeSet/cdk-deploy-change-set/82a2627a-c17b-4c4a-8d8c-2cb8c5dc3470",
                    "Parameters": [
                        {
                            "ParameterKey": "AssetParametersfd68488e1fd8c565219e0163590a33c90ee2fb16a5b983b28af510f531e3929dArtifactHash2B687F73",
                            "ParameterValue": "fd68488e1fd8c565219e0163590a33c90ee2fb16a5b983b28af510f531e3929d",
                        },
                        {
                            "ParameterKey": "AssetParametersfd68488e1fd8c565219e0163590a33c90ee2fb16a5b983b28af510f531e3929dS3BucketA554ADF4",
                            "ParameterValue": "cdktoolkit-stagingbucket-1r42id4mzo7q0",
                        },
                        {
                            "ParameterKey": "AssetParametersfd68488e1fd8c565219e0163590a33c90ee2fb16a5b983b28af510f531e3929dS3VersionKey75C480A9",
                            "ParameterValue": "assets/||fd68488e1fd8c565219e0163590a33c90ee2fb16a5b983b28af510f531e3929d.zip",
                        },
                    ],
                    "CreationTime": datetime.datetime(2021, 7, 22, 9, 38, 30, 216000),
                    "LastUpdatedTime": datetime.datetime(
                        2021, 7, 23, 12, 28, 32, 460000
                    ),
                    "RollbackConfiguration": {},
                    "StackStatus": "UPDATE_COMPLETE",
                    "DisableRollback": False,
                    "NotificationARNs": [],
                    "Capabilities": [
                        "CAPABILITY_IAM",
                        "CAPABILITY_NAMED_IAM",
                        "CAPABILITY_AUTO_EXPAND",
                    ],
                    "Outputs": [
                        {
                            "OutputKey": "DatajobExecutionInput",
                            "OutputValue": '["datajob-ml-pipeline-scikitlearn-processing-job", "datajob-ml-pipeline-scikitlearn-training-job"]',
                        }
                    ],
                    "Tags": [],
                    "EnableTerminationProtection": False,
                    "DriftInformation": {"StackDriftStatus": "NOT_CHECKED"},
                }
            ],
            "ResponseMetadata": {
                "RequestId": "b5ea17e1-9891-45f3-9886-082f5a577520",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {
                    "x-amzn-requestid": "b5ea17e1-9891-45f3-9886-082f5a577520",
                    "content-type": "text/xml",
                    "content-length": "2556",
                    "vary": "accept-encoding",
                    "date": "Mon, 26 Jul 2021 20:08:09 GMT",
                },
                "RetryAttempts": 0,
            },
        }
