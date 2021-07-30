import pathlib
import unittest
from datetime import datetime
from unittest import mock

from aws_cdk import core
from moto import mock_s3
from moto import mock_sagemaker
from sagemaker import LocalSession
from sagemaker.sklearn import SKLearnProcessor
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.transformer import Transformer

from datajob.datajob_stack import DataJobStack
from datajob.sagemaker import DataJobSagemakerBase
from datajob.sagemaker.sagemaker_job import ProcessingStep
from datajob.sagemaker.sagemaker_job import TrainingStep
from datajob.sagemaker.sagemaker_job import TransformStep
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow

current_dir = pathlib.Path(__file__).parent.absolute()


class TestSagemaker(unittest.TestCase):
    def setUp(self) -> None:
        self.app = core.App()

    @mock.patch("sagemaker.session.Session.default_bucket")
    def test_sagemaker_services_successfully(self):
        role = "arn:aws:iam::111111111111:role/service-role/AmazonSageMaker-ExecutionRole-20200101T000001"
        sagemaker_session = LocalSession()
        sagemaker_session.config = {"local": {"local_code": True}}

        with DataJobStack(scope=self.app, id="some-stack", stage="stg") as djs:

            processor = SKLearnProcessor(
                framework_version="0.23-1",
                role=role,
                instance_type="local",
                instance_count=1,
                sagemaker_session=sagemaker_session,
            )

            processing_step = ProcessingStep(
                datajob_stack=djs,
                name="processing-job",
                processor=processor,
            )

            estimator = SKLearn(
                entry_point=str(pathlib.Path(current_dir, "resources", "train.py")),
                train_instance_type="ml.m5.xlarge",
                role=role,
                framework_version="0.20.0",
                py_version="py3",
                sagemaker_session=sagemaker_session,
            )

            training_step = TrainingStep(
                datajob_stack=djs,
                name="training-job",
                estimator=estimator,
            )

            transformer = Transformer(
                model_name=training_step.sfn_task.get_expected_model(),
                instance_count=1,
                instance_type="ml.t2.medium",
                sagemaker_session=sagemaker_session,
            )
            transform_step = TransformStep(
                datajob_stack=djs,
                name="transform-job",
                transformer=transformer,
                data="s3://some-bucket/some-data.csv",
            )
            with StepfunctionsWorkflow(djs, "sequential") as sfn_workflow:
                processing_step >> training_step >> transform_step

            with StepfunctionsWorkflow(djs, "parallel") as sfn_workflow:
                processing_step >> processing_step
                training_step >> training_step

        # check if we have the expected value for the execution input
        self.assertDictEqual(
            DataJobSagemakerBase.execution_input_schema,
            {"some-stack-stg-processing-job": str, "some-stack-stg-training-job": str},
        )
        # execution input is added to cloudformation output
        self.assertDictEqual(
            djs.outputs,
            {
                "DatajobExecutionInput": '["some-stack-stg-processing-job", "some-stack-stg-training-job"]'
            },
        )

    def test_generate_unique_name_successfully(self):
        # freeze time
        DataJobSagemakerBase.current_date = datetime(2021, 1, 1, 12, 0, 1)
        # test with a long string and check that the result will be max allowed characters
        unique_name = DataJobSagemakerBase.generate_unique_name(
            name="a" * DataJobSagemakerBase.MAX_CHARS
        )
        self.assertEqual(len(unique_name), DataJobSagemakerBase.MAX_CHARS)

        # test with a short string and check that the datetime will be appended
        unique_name = DataJobSagemakerBase.generate_unique_name(name="a" * 1)
        self.assertEqual(unique_name, "a-20210101T120001")


if __name__ == "__main__":
    unittest.main()
