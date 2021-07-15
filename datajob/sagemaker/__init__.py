from datetime import datetime

from aws_cdk import aws_iam as iam
from sagemaker import estimator
from sagemaker import processing
from stepfunctions.inputs import Placeholder
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
    current_date = datetime.utcnow()
    MAX_CHARS = 63
    execution_input = {}

    @staticmethod
    def generate_unique_name(
        name: str, max_chars: int = MAX_CHARS, datetime_format: str = "%Y%m%dT%H%M%S"
    ):
        if not isinstance(name, Placeholder):
            current_date_as_string = DatajobSagemakerBase.current_date.strftime(
                datetime_format
            )
            total_length = len(current_date_as_string) + len(name)
            difference = max_chars - total_length
            if difference < 0:
                logger.debug(
                    f"the length of the unique name is {total_length}. Max chars is {max_chars}. Removing last {difference} chars from name"
                )
                name = name[: difference - 1]
            unique_name = f"{name}-{current_date_as_string}"
            logger.debug(f"generated unique name is {unique_name}")
            return unique_name
        logger.debug("name is a stepfunctions placeholder value, returning")

    def handle_job_name(self, job_name):
        """

        Args:
            job_name:

        Returns:

        """
        if job_name is None:
            logger.debug(
                f"job name not provided, we will return the unique name {self.unique_name}"
            )
            return self.generate_unique_name(self.unique_name)
        elif isinstance(job_name, Placeholder):
            logger.debug(
                f"job_name is an isntance of stepfunctions placeholder, we will return the placeholder"
            )
            return job_name
        else:
            return job_name

    def create(self):
        logger.debug(
            "sagemaker does not implement the create "
            "function because it's not necessary/not supported to add these services to the stack."
        )

    def get_default_role(self, name: str) -> iam.Role:
        name += "-sagemaker"
        return self._get_default_role(name, "sagemaker.amazonaws.com")


class TrainingStep(DatajobSagemakerBase):
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
        **kwargs,
    ):
        DatajobSagemakerBase.__init__(
            self=self, datajob_stack=datajob_stack, name=name, **kwargs
        )
        self.sfn_task = SagemakerTrainingStep(
            state_id=self.unique_name if state_id is None else state_id,
            estimator=estimator,
            job_name=self.handle_job_name(job_name),
            data=data,
            hyperparameters=hyperparameters,
            mini_batch_size=mini_batch_size,
            experiment_config=experiment_config,
            wait_for_completion=wait_for_completion,
            tags=tags,
            output_data_config_path=output_data_config_path,
            **kwargs,
        )


class ProcessingStep(DatajobSagemakerBase):
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
        **kwargs,
    ):
        DatajobSagemakerBase.__init__(
            self=self, datajob_stack=datajob_stack, name=name, **kwargs
        )

        self.sfn_task = SagemakerProcessingStep(
            state_id=self.unique_name if state_id is None else state_id,
            processor=processor,
            job_name=self.handle_job_name(job_name),
            inputs=inputs,
            outputs=outputs,
            experiment_config=experiment_config,
            container_arguments=container_arguments,
            container_entrypoint=container_entrypoint,
            kms_key_id=kms_key_id,
            wait_for_completion=wait_for_completion,
            tags=tags,
            **kwargs,
        )


class TransformStep(SagemakerTransformStep, DatajobSagemakerBase):
    pass


class TuningStep(SagemakerTuningStep, DatajobSagemakerBase):
    pass


class ModelStep(SagemakerModelStep, DatajobSagemakerBase):
    pass


class EndpointStep(SagemakerEndpointStep, DatajobSagemakerBase):
    pass


class EndpointConfigStep(SagemakerEndpointConfigStep, DatajobSagemakerBase):
    pass
