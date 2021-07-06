from aws_cdk import aws_iam as iam
from sagemaker import estimator
from sagemaker import processing
from stepfunctions.steps.sagemaker import (
    EndpointConfigStep as SagemakerEndpointConfigStep,
)
from stepfunctions.steps.sagemaker import EndpointStep as SagemakerEndpointStep
from stepfunctions.steps.sagemaker import ModelStep as SagemakerModelStep
from stepfunctions.steps.sagemaker import ProcessingStep as SagemakerProcessingStep
from stepfunctions.steps.sagemaker import TrainingStep as SagemakerTrainingStep
from stepfunctions.steps.sagemaker import TransformStep as SagemakerTransformStep
from stepfunctions.steps.sagemaker import TuningStep as SagemakerTuningStep

from datajob import logger
from datajob.datajob_base import DataJobBase
from datajob.datajob_stack import DataJobStack
from datajob.stepfunctions import stepfunctions_workflow


@stepfunctions_workflow.task
class DatajobSagemakerBase(DataJobBase):
    def create(self):
        logger.debug(
            "sagemaker does not implement the create "
            "function because it's not necessary/not supported to add these services to the stack."
        )

    def get_default_role(self, name: str) -> iam.Role:
        name = name + "-sagemaker"
        return self._get_default_role(name, "sagemaker.amazonaws.com")

    def __repr__(self):
        return "{}".format(
            self.__class__.__name__,
        )

    def __str__(self):
        return "{}".format(
            self.__class__.__name__,
        )


class TrainingStep(DatajobSagemakerBase, SagemakerTrainingStep):
    def __init__(
        self,
        datajob_stack: DataJobStack,
        name: str,
        estimator: estimator.EstimatorBase,
        state_id=None,
        job_name=None,
        data=None,
        hyperparameters=None,
        mini_batch_size=None,
        experiment_config=None,
        wait_for_completion=True,
        tags=None,
        output_data_config_path=None,
        **kwargs
    ):
        DatajobSagemakerBase.__init__(
            self=self, datajob_stack=datajob_stack, name=name, **kwargs
        )
        self.sfn_task = SagemakerTrainingStep(
            state_id=self.unique_name if state_id is None else state_id,
            estimator=estimator,
            job_name=self.unique_name if job_name is None else job_name,
            data=data,
            hyperparameters=hyperparameters,
            mini_batch_size=mini_batch_size,
            experiment_config=experiment_config,
            wait_for_completion=wait_for_completion,
            tags=tags,
            output_data_config_path=output_data_config_path,
            **kwargs
        )


class ProcessingStep(DatajobSagemakerBase, SagemakerProcessingStep):
    def __init__(
        self,
        datajob_stack: DataJobStack,
        name: str,
        processor: processing.Processor,
        state_id=None,
        job_name=None,
        inputs=None,
        outputs=None,
        experiment_config=None,
        container_arguments=None,
        container_entrypoint=None,
        kms_key_id=None,
        wait_for_completion=True,
        tags=None,
        **kwargs
    ):
        DatajobSagemakerBase.__init__(
            self=self, datajob_stack=datajob_stack, name=name, **kwargs
        )

        self.sfn_task = SagemakerProcessingStep(
            state_id=self.unique_name if state_id is None else state_id,
            processor=processor,
            job_name=self.unique_name if job_name is None else job_name,
            inputs=inputs,
            outputs=outputs,
            experiment_config=experiment_config,
            container_arguments=container_arguments,
            container_entrypoint=container_entrypoint,
            kms_key_id=kms_key_id,
            wait_for_completion=wait_for_completion,
            tags=tags,
            **kwargs
        )


class TransformStep(DatajobSagemakerBase, SagemakerTransformStep):
    pass


class TuningStep(DatajobSagemakerBase, SagemakerTuningStep):
    pass


class ModelStep(DatajobSagemakerBase, SagemakerModelStep):
    pass


class EndpointStep(DatajobSagemakerBase, SagemakerEndpointStep):
    pass


class EndpointConfigStep(DatajobSagemakerBase, SagemakerEndpointConfigStep):
    pass
