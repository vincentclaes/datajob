from unittest import mock
import datetime
from datajob.stepfunctions import stepfunctions_run
import unittest


class TestStepFunctionsRun(unittest.TestCase):
    @mock.patch("datajob.stepfunctions.stepfunctions_run._get_cloudformation_resource")
    def test_datajob_run_recursive_until_no_next_token(self, m_cf_resources):
        mock_cloudformation_summary_next_token = mock_cloudformation_summary.copy()
        mock_cloudformation_summary_next_token["NextToken"] = "SomeToken"
        m_cf_resources.side_effect = [
            mock_cloudformation_summary_next_token,
            mock_cloudformation_summary_next_token,
            mock_cloudformation_summary,
        ]
        resources = stepfunctions_run._get_all_cloudformation_resources("some-stack")
        self.assertEqual(len(resources), 24)  # 3 * 6 resources


mock_cloudformation_summary = {
    "StackResourceSummaries": [
        {
            "LogicalResourceId": "zippodatalayerstgzippodatalayerstgdeploymentbucketB3019285",
            "PhysicalResourceId": "zippo-data-layer-stg-deployment-bucket",
            "ResourceType": "AWS::S3::Bucket",
            "LastUpdatedTimestamp": datetime.datetime(2011, 6, 21, 20, 15, 58),
            "ResourceStatus": "CREATE_COMPLETE",
        },
        {
            "LogicalResourceId": "dumpdisplaynamestogbqzippodatalayerstgdumpdisplaynamestogbqroleB8262B3A",
            "PhysicalResourceId": "pze7m6zn4pue3xjvi15p",
            "ResourceType": "AWS::IAM::Role",
            "LastUpdatedTimestamp": datetime.datetime(2011, 6, 21, 20, 15, 58),
            "ResourceStatus": "CREATE_COMPLETE",
        },
        {
            "LogicalResourceId": "",
            "PhysicalResourceId": "",
            "ResourceType": "",
            "LastUpdatedTimestamp": datetime.datetime(2011, 6, 21, 20, 15, 58),
            "ResourceStatus": "CREATE_COMPLETE",
        },
        {
            "LogicalResourceId": "zippodatalayerzippodatalayerstgzippodatalayerrole5D9A59C6",
            "PhysicalResourceId": "01k0rq3yyc2djjje31nz",
            "ResourceType": "AWS::IAM::Role",
            "LastUpdatedTimestamp": datetime.datetime(2011, 6, 21, 20, 15, 58),
            "ResourceStatus": "CREATE_COMPLETE",
        },
        {
            "LogicalResourceId": "",
            "PhysicalResourceId": "",
            "ResourceType": "",
            "LastUpdatedTimestamp": datetime.datetime(2011, 6, 21, 20, 15, 58),
            "ResourceStatus": "CREATE_COMPLETE",
        },
        {
            "LogicalResourceId": "",
            "PhysicalResourceId": "",
            "ResourceType": "",
            "LastUpdatedTimestamp": datetime.datetime(2011, 6, 21, 20, 15, 58),
            "ResourceStatus": "CREATE_COMPLETE",
        },
    ],
    "ResponseMetadata": {
        "RequestId": "2d06e36c-ac1d-11e0-a958-f9382b6eb86b",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {"server": "amazon.com"},
        "RetryAttempts": 0,
    },
}
