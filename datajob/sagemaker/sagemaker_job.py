from sagemaker import estimator
from sagemaker import processing
from stepfunctions.steps import EndpointConfigStep as SagemakerEndpointConfigStep
from stepfunctions.steps import EndpointStep as SagemakerEndpointStep
from stepfunctions.steps import ModelStep as SagemakerModelStep
from stepfunctions.steps import ProcessingStep as SagemakerProcessingStep
from stepfunctions.steps import TrainingStep as SagemakerTrainingStep
from stepfunctions.steps import TransformStep as SagemakerTransformStep
from stepfunctions.steps import TuningStep as SagemakerTuningStep

from datajob.datajob_stack import DataJobStack
from datajob.sagemaker import DataJobSagemakerBase
from datajob.stepfunctions import stepfunctions_workflow


@stepfunctions_workflow.task
class TrainingStep(DataJobSagemakerBase):
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
        DataJobSagemakerBase.__init__(
            self=self, datajob_stack=datajob_stack, name=name, **kwargs
        )
        self.sfn_task = SagemakerTrainingStep(
            state_id=self.unique_name if state_id is None else state_id,
            estimator=estimator,
            job_name=self.handle_argument_for_execution_input(
                datajob_stack=datajob_stack, argument=job_name
            ),
            data=data,
            hyperparameters=hyperparameters,
            mini_batch_size=mini_batch_size,
            experiment_config=experiment_config,
            wait_for_completion=wait_for_completion,
            tags=tags,
            output_data_config_path=output_data_config_path,
            **kwargs,
        )


@stepfunctions_workflow.task
class ProcessingStep(DataJobSagemakerBase):
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
        DataJobSagemakerBase.__init__(
            self=self, datajob_stack=datajob_stack, name=name, **kwargs
        )

        self.sfn_task = SagemakerProcessingStep(
            state_id=self.unique_name if state_id is None else state_id,
            processor=processor,
            job_name=self.handle_argument_for_execution_input(
                datajob_stack=datajob_stack, argument=job_name
            ),
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


@stepfunctions_workflow.task
class TransformStep(SagemakerTransformStep, DataJobSagemakerBase):
    pass


@stepfunctions_workflow.task
class TuningStep(SagemakerTuningStep, DataJobSagemakerBase):
    pass


@stepfunctions_workflow.task
class ModelStep(SagemakerModelStep, DataJobSagemakerBase):
    pass


@stepfunctions_workflow.task
class EndpointStep(SagemakerEndpointStep, DataJobSagemakerBase):
    pass


@stepfunctions_workflow.task
class EndpointConfigStep(SagemakerEndpointConfigStep, DataJobSagemakerBase):
    pass
