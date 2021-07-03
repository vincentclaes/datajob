from stepfunctions.steps.sagemaker import EndpointConfigStep
from stepfunctions.steps.sagemaker import EndpointStep
from stepfunctions.steps.sagemaker import ModelStep
from stepfunctions.steps.sagemaker import ProcessingStep
from stepfunctions.steps.sagemaker import TrainingStep
from stepfunctions.steps.sagemaker import TransformStep
from stepfunctions.steps.sagemaker import TuningStep

from datajob import logger
from datajob.datajob_base import DataJobBase
from datajob.stepfunctions import stepfunctions_workflow


@stepfunctions_workflow.task
class DatajobSagemakerBase(DataJobBase):
    def create(self):
        logger.debug(
            "sagemaker does not implement the create "
            "function because it's not necessary/not supported to add these services to the stack."
        )


class TrainingStep(DatajobSagemakerBase, TrainingStep):
    pass


class TransformStep(DatajobSagemakerBase, TransformStep):
    pass


class ProcessingStep(DatajobSagemakerBase, ProcessingStep):
    pass


class TuningStep(DatajobSagemakerBase, TuningStep):
    pass


class ModelStep(DatajobSagemakerBase, ModelStep):
    pass


class EndpointStep(DatajobSagemakerBase, EndpointStep):
    pass


class EndpointConfigStep(DatajobSagemakerBase, EndpointConfigStep):
    pass
