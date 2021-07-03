import unittest

from aws_cdk import core
from sagemaker import LocalSession
from sagemaker.sklearn import SKLearnProcessor
from sagemaker.sklearn.estimator import SKLearn

from datajob.datajob_stack import DataJobStack
from datajob.sagemaker import ProcessingStep
from datajob.sagemaker import TrainingStep


class TestSagemaker(unittest.TestCase):
    def setUp(self) -> None:
        self.app = core.App()

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
            )

            processing_step = ProcessingStep(
                state_id="processing-job",
                processor=processor,
                job_name="processing-job",
            )

            estimator = SKLearn(
                entry_point="resources/train.py",
                train_instance_type="ml.m5.xlarge",
                role=role,
                framework_version="0.20.0",
                py_version="py3",
            )

            training_step = TrainingStep(
                state_id="training-job", estimator=estimator, job_name="training-job"
            )

            with StepfunctionsWorkflow(djs, "some-name") as a_step_functions_workflow:
                processing_step >> training_step


if __name__ == "__main__":
    unittest.main()
