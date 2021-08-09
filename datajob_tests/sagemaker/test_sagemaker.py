import json
import pathlib
import unittest
from unittest import mock

from aws_cdk import core
from sagemaker import LocalSession
from sagemaker.parameter import ContinuousParameter
from sagemaker.sklearn import SKLearnProcessor
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.transformer import Transformer
from sagemaker.tuner import HyperparameterTuner

from datajob.datajob_stack import DataJobStack
from datajob.sagemaker.sagemaker_job import EndpointConfigStep
from datajob.sagemaker.sagemaker_job import EndpointStep
from datajob.sagemaker.sagemaker_job import ModelStep
from datajob.sagemaker.sagemaker_job import ProcessingStep
from datajob.sagemaker.sagemaker_job import TrainingStep
from datajob.sagemaker.sagemaker_job import TransformStep
from datajob.sagemaker.sagemaker_job import TuningStep
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow

current_dir = pathlib.Path(__file__).parent.absolute()


class TestSagemaker(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.role = "arn:aws:iam::111111111111:role/service-role/AmazonSageMaker-ExecutionRole-20200101T000001"

        cls.sagemaker_session = LocalSession()
        cls.sagemaker_session.config = {"local": {"local_code": True}}

    def setUp(self) -> None:
        self.app = core.App()

    @mock.patch("sagemaker.session.Session.default_bucket")
    def test_sagemaker_services_successfully(self, m_default_bucket):

        m_default_bucket.return_value = "sagemaker-bucket-name"

        with DataJobStack(scope=self.app, id="some-stack", stage="stg") as djs:

            processor = SKLearnProcessor(
                framework_version="0.23-1",
                role=self.role,
                instance_type="local",
                instance_count=1,
                sagemaker_session=self.sagemaker_session,
            )

            processing_step = ProcessingStep(
                datajob_stack=djs,
                name="processing-job",
                processor=processor,
            )

            estimator = SKLearn(
                entry_point=str(pathlib.Path(current_dir, "resources", "train.py")),
                train_instance_type="ml.m5.xlarge",
                role=self.role,
                framework_version="0.20.0",
                py_version="py3",
                sagemaker_session=self.sagemaker_session,
            )

            training_step = TrainingStep(
                datajob_stack=djs,
                name="training-job",
                estimator=estimator,
            )

            model_step = ModelStep(
                datajob_stack=djs,
                name="model-step",
                model=training_step.sfn_task.get_expected_model(),
            )

            endpoint_config_step = EndpointConfigStep(
                datajob_stack=djs,
                name="endpoint-config-step",
                model_name=model_step.model_name,
            )

            endpoint_step = EndpointStep(
                datajob_stack=djs,
                name="endpoint-step",
                endpoint_config_name=endpoint_config_step.name,
            )

            with StepfunctionsWorkflow(djs, "sequential") as sfn_workflow_sequential:
                (
                    processing_step
                    >> training_step
                    >> model_step
                    >> endpoint_config_step
                    >> endpoint_step
                )

            with StepfunctionsWorkflow(djs, "parallel") as sfn_workflow_parallel:
                processing_step >> processing_step
                training_step >> training_step

        # check if we have the expected value for the execution input
        self.assertDictEqual(
            djs.execution_input.execution_input_schema,
            {
                "some-stack-stg-processing-job": str,
                "some-stack-stg-training-job": str,
                "some-stack-stg-model-step": str,
                "some-stack-stg-endpoint-config-step": str,
                "some-stack-stg-endpoint-step": str,
            },
        )
        # execution input is added to cloudformation output
        self.assertDictEqual(
            djs.outputs,
            {
                "DatajobExecutionInput": json.dumps(
                    [
                        "some-stack-stg-processing-job",
                        "some-stack-stg-training-job",
                        "some-stack-stg-model-step",
                        "some-stack-stg-endpoint-config-step",
                        "some-stack-stg-endpoint-step",
                    ]
                )
            },
        )

    @mock.patch("sagemaker.session.Session.default_bucket")
    def test_sagemaker_transform_step_successfully(self, m_default_bucket):

        m_default_bucket.return_value = "sagemaker-bucket-name"

        with DataJobStack(scope=self.app, id="some-stack", stage="stg") as djs:
            transformer = Transformer(
                model_name="some-model",
                instance_count=1,
                instance_type="ml.t2.medium",
                sagemaker_session=self.sagemaker_session,
            )

            transform_step = TransformStep(
                datajob_stack=djs,
                name="transform-job",
                transformer=transformer,
                data="s3://some-bucket/some-data.csv",
            )

            estimator = SKLearn(
                entry_point=str(pathlib.Path(current_dir, "resources", "train.py")),
                train_instance_type="ml.m5.xlarge",
                role=self.role,
                framework_version="0.20.0",
                py_version="py3",
                sagemaker_session=self.sagemaker_session,
            )

            tuner = HyperparameterTuner(
                estimator=estimator,
                hyperparameter_ranges={"alpha": ContinuousParameter(0.0001, 0.05)},
                objective_metric_name="rmse",
            )

            tuner_step = TuningStep(
                datajob_stack=djs,
                name="tuning-step",
                tuner=tuner,
                data="s3://some-bucket/some-data.csv",
            )

            with StepfunctionsWorkflow(djs, "sequential") as sfn_workflow:
                transform_step >> tuner_step


if __name__ == "__main__":
    unittest.main()
