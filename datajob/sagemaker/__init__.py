from stepfunctions.steps.sagemaker import EndpointConfigStep
from stepfunctions.steps.sagemaker import EndpointStep
from stepfunctions.steps.sagemaker import ModelStep
from stepfunctions.steps.sagemaker import ProcessingStep
from stepfunctions.steps.sagemaker import TrainingStep
from stepfunctions.steps.sagemaker import TransformStep
from stepfunctions.steps.sagemaker import TuningStep

from datajob import logger
from datajob.datajob_base import DataJobBase


class DatajobSagemakerBase(DataJobBase):
    def create(self):
        logger.debug(
            "sagemaker does not implement the create "
            "function because it's not necessary/not supported to add these services to the stack."
        )


class TrainingStep(TrainingStep, DatajobSagemakerBase):
    pass


class TransformStep(TransformStep, DatajobSagemakerBase):
    pass


class ProcessingStep(ProcessingStep, DatajobSagemakerBase):
    pass


class TuningStep(TuningStep, DatajobSagemakerBase):
    pass


class ModelStep(ModelStep, DataJobBase):
    pass


class EndpointStep(EndpointStep, DataJobBase):
    pass


class EndpointConfigStep(EndpointConfigStep, DataJobBase):
    pass
