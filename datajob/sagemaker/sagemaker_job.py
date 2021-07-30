from sagemaker import estimator
from sagemaker import processing
from sagemaker import transformer
from sagemaker.tuner import HyperparameterTuner
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
class TransformStep(DataJobSagemakerBase):
    def __init__(
        self,
        datajob_stack: DataJobStack,
        name: str,
        transformer: transformer.Transformer,
        data,
        model_name=None,
        job_name=None,
        state_id: str = None,
        data_type="S3Prefix",
        content_type=None,
        compression_type=None,
        split_type=None,
        experiment_config=None,
        wait_for_completion=True,
        tags=None,
        input_filter=None,
        output_filter=None,
        join_source=None,
        **kwargs,
    ):
        DataJobSagemakerBase.__init__(
            self=self, datajob_stack=datajob_stack, name=name, **kwargs
        )
        self.sfn_task = SagemakerTransformStep(
            state_id=self.unique_name if state_id is None else state_id,
            transformer=transformer,
            job_name=self.handle_argument_for_execution_input(
                datajob_stack=datajob_stack, argument=job_name
            ),
            model_name=transformer.model_name if model_name is None else model_name,
            data=data,
            data_type=data_type,
            content_type=content_type,
            compression_type=compression_type,
            split_type=split_type,
            experiment_config=experiment_config,
            wait_for_completion=wait_for_completion,
            tags=tags,
            input_filter=input_filter,
            output_filter=output_filter,
            join_source=join_source,
            **kwargs,
        )


@stepfunctions_workflow.task
class TuningStep(DataJobSagemakerBase):
    def __init__(
        self,
        datajob_stack: DataJobStack,
        name: str,
        tuner: HyperparameterTuner,
        job_name: any,
        data: any,
        state_id: str = None,
        wait_for_completion=True,
        tags=None,
        **kwargs,
    ):
        DataJobSagemakerBase.__init__(
            self=self, datajob_stack=datajob_stack, name=name, **kwargs
        )
        self.sfn_task = SagemakerTuningStep(
            state_id=self.unique_name if state_id is None else state_id,
            tuner=tuner,
            job_name=self.handle_argument_for_execution_input(
                datajob_stack=datajob_stack, argument=job_name
            ),
            data=data,
            wait_for_completion=wait_for_completion,
            tags=tags,
            **kwargs,
        )


@stepfunctions_workflow.task
class ModelStep(DataJobSagemakerBase):
    def __init__(
        self,
        datajob_stack: DataJobStack,
        name: str,
        model: str,
        state_id=None,
        model_name=None,
        instance_type=None,
        tags=None,
        **kwargs,
    ):
        DataJobSagemakerBase.__init__(
            self=self, datajob_stack=datajob_stack, name=name, **kwargs
        )

        self.sfn_task = SagemakerModelStep(
            state_id=self.unique_name if state_id is None else state_id,
            model=model,
            model_name=self.handle_argument_for_execution_input(
                datajob_stack=datajob_stack, argument=model_name
            ),
            instance_type=instance_type,
            tags=tags,
            **kwargs,
        )


@stepfunctions_workflow.task
class EndpointStep(DataJobSagemakerBase):
    def __init__(
        self,
        datajob_stack: DataJobStack,
        name: str,
        endpoint_config_name: str,
        state_id=None,
        endpoint_name=None,
        tags=None,
        update=False,
        **kwargs,
    ):
        DataJobSagemakerBase.__init__(
            self=self, datajob_stack=datajob_stack, name=name, **kwargs
        )

        self.sfn_task = SagemakerEndpointStep(
            state_id=self.unique_name if state_id is None else state_id,
            endpoint_name=self.handle_argument_for_execution_input(
                datajob_stack=datajob_stack, argument=endpoint_name
            ),
            endpoint_config_name=endpoint_config_name,
            tags=tags,
            update=update,
            **kwargs,
        )


@stepfunctions_workflow.task
class EndpointConfigStep(DataJobSagemakerBase):
    def __init__(
        self,
        datajob_stack: DataJobStack,
        name: str,
        model_name: str,
        state_id=None,
        endpoint_config_name=None,
        initial_instance_count=1,
        instance_type="ml.t2.medium",
        variant_name="AllTraffic",
        data_capture_config=None,
        tags=None,
        **kwargs,
    ):
        DataJobSagemakerBase.__init__(
            self=self, datajob_stack=datajob_stack, name=name, **kwargs
        )

        self.sfn_task = SagemakerEndpointConfigStep(
            state_id=state_id,
            endpoint_config_name=self.handle_argument_for_execution_input(
                datajob_stack=datajob_stack, argument=endpoint_config_name
            ),
            model_name=model_name,
            initial_instance_count=initial_instance_count,
            instance_type=instance_type,
            variant_name=variant_name,
            data_capture_config=data_capture_config,
            tags=tags,
            **kwargs,
        )
