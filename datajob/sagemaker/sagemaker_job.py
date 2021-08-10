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

        self.state_id = self.unique_name if state_id is None else state_id
        self.estimator = estimator
        self.job_name = (
            datajob_stack.execution_input.handle_argument_for_execution_input(
                datajob_stack=datajob_stack,
                argument=job_name,
                unique_name=self.unique_name,
            )
        )
        self.data = data
        self.hyperparameters = hyperparameters
        self.mini_batch_size = mini_batch_size
        self.experiment_config = experiment_config
        self.wait_for_completion = wait_for_completion
        self.tags = tags

        self.sfn_task = SagemakerTrainingStep(
            state_id=self.state_id,
            estimator=self.estimator,
            job_name=self.job_name,
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

        self.state_id = self.unique_name if state_id is None else state_id
        self.processor = processor
        self.job_name = (
            datajob_stack.execution_input.handle_argument_for_execution_input(
                datajob_stack=datajob_stack,
                argument=job_name,
                unique_name=self.unique_name,
            )
        )
        self.inputs = inputs
        self.outputs = outputs
        self.experiment_config = experiment_config
        self.container_arguments = container_arguments
        self.container_entrypoint = container_entrypoint
        self.kms_key_id = kms_key_id
        self.wait_for_completion = wait_for_completion
        self.tags = tags

        self.sfn_task = SagemakerProcessingStep(
            state_id=self.state_id,
            processor=self.processor,
            job_name=self.job_name,
            inputs=self.inputs,
            outputs=self.outputs,
            experiment_config=self.experiment_config,
            container_arguments=self.container_arguments,
            container_entrypoint=self.container_entrypoint,
            kms_key_id=self.kms_key_id,
            wait_for_completion=self.wait_for_completion,
            tags=self.tags,
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

        self.state_id = self.unique_name if state_id is None else state_id
        self.transformer = transformer
        self.job_name = (
            datajob_stack.execution_input.handle_argument_for_execution_input(
                datajob_stack=datajob_stack,
                argument=job_name,
                unique_name=self.unique_name,
            )
        )
        self.model_name = transformer.model_name if model_name is None else model_name
        self.data = data
        self.data_type = data_type
        self.content_type = content_type
        self.compression_type = compression_type
        self.split_type = split_type
        self.experiment_config = experiment_config
        self.wait_for_completion = wait_for_completion
        self.tags = tags
        self.input_filter = input_filter
        self.output_filter = output_filter
        self.join_source = join_source

        self.sfn_task = SagemakerTransformStep(
            state_id=self.state_id,
            transformer=self.transformer,
            job_name=self.job_name,
            model_name=self.model_name,
            data=self.data,
            data_type=self.data_type,
            content_type=self.content_type,
            compression_type=self.compression_type,
            split_type=self.split_type,
            experiment_config=self.experiment_config,
            wait_for_completion=self.wait_for_completion,
            tags=self.tags,
            input_filter=self.input_filter,
            output_filter=self.output_filter,
            join_source=self.join_source,
            **kwargs,
        )


@stepfunctions_workflow.task
class TuningStep(DataJobSagemakerBase):
    def __init__(
        self,
        datajob_stack: DataJobStack,
        name: str,
        tuner: HyperparameterTuner,
        data: any,
        job_name: any = None,
        state_id: str = None,
        wait_for_completion=True,
        tags=None,
        **kwargs,
    ):
        DataJobSagemakerBase.__init__(
            self=self, datajob_stack=datajob_stack, name=name, **kwargs
        )
        self.state_id = self.unique_name if state_id is None else state_id
        self.tuner = tuner
        self.job_name = (
            datajob_stack.execution_input.handle_argument_for_execution_input(
                datajob_stack=datajob_stack,
                argument=job_name,
                unique_name=self.unique_name,
            )
        )
        self.data = data
        self.wait_for_completion = wait_for_completion
        self.tags = tags
        self.sfn_task = SagemakerTuningStep(
            state_id=self.state_id,
            tuner=self.tuner,
            job_name=self.job_name,
            data=self.data,
            wait_for_completion=self.wait_for_completion,
            tags=self.tags,
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
        self.state_id = self.unique_name if state_id is None else state_id
        self.model = model
        self.model_name = (
            datajob_stack.execution_input.handle_argument_for_execution_input(
                datajob_stack=datajob_stack,
                argument=model_name,
                unique_name=self.unique_name,
            )
        )
        self.instance_type = instance_type
        self.tags = tags
        self.sfn_task = SagemakerModelStep(
            state_id=self.state_id,
            model=self.model,
            model_name=self.model_name,
            instance_type=self.instance_type,
            tags=self.tags,
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
        self.state_id = self.unique_name if state_id is None else state_id
        self.endpoint_config_name = (
            datajob_stack.execution_input.handle_argument_for_execution_input(
                datajob_stack=datajob_stack,
                argument=endpoint_config_name,
                unique_name=self.unique_name,
            )
        )
        self.model_name = model_name
        self.initial_instance_count = initial_instance_count
        self.instance_type = instance_type
        self.variant_name = variant_name
        self.data_capture_config = data_capture_config
        self.tags = tags
        self.sfn_task = SagemakerEndpointConfigStep(
            state_id=self.state_id,
            endpoint_config_name=self.endpoint_config_name,
            model_name=self.model_name,
            initial_instance_count=self.initial_instance_count,
            instance_type=self.instance_type,
            variant_name=self.variant_name,
            data_capture_config=self.data_capture_config,
            tags=self.tags,
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
        self.state_id = self.unique_name if state_id is None else state_id
        self.endpoint_name = (
            datajob_stack.execution_input.handle_argument_for_execution_input(
                datajob_stack=datajob_stack,
                argument=endpoint_name,
                unique_name=self.unique_name,
            )
        )
        self.endpoint_config_name = endpoint_config_name
        self.tags = tags
        self.update = update
        self.sfn_task = SagemakerEndpointStep(
            state_id=self.state_id,
            endpoint_name=self.endpoint_name,
            endpoint_config_name=self.endpoint_config_name,
            tags=self.tags,
            update=self.update,
            **kwargs,
        )
