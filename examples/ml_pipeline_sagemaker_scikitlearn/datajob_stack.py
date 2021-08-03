"""https://github.com/aws/amazon-sagemaker-examples/blob/master/step-functions-
data-science-sdk/step_functions_mlworkflow_processing/step_functions_mlworkflow
_scikit_learn_data_processing_and_model_evaluation.ipynb."""
import boto3
import sagemaker
from aws_cdk import core
from sagemaker.processing import ProcessingInput
from sagemaker.processing import ProcessingOutput
from sagemaker.sklearn import SKLearnProcessor
from sagemaker.sklearn.estimator import SKLearn

from datajob.datajob_stack import DataJobStack
from datajob.sagemaker.sagemaker_job import EndpointConfigStep
from datajob.sagemaker.sagemaker_job import EndpointStep
from datajob.sagemaker.sagemaker_job import ModelStep
from datajob.sagemaker.sagemaker_job import ProcessingStep
from datajob.sagemaker.sagemaker_job import TrainingStep
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow

role = "arn:aws:iam::077590795309:role/service-role/AmazonSageMaker-ExecutionRole-20191008T190827"
app = core.App()


with DataJobStack(scope=app, id="datajob-ml-pipeline-scikitlearn") as djs:

    sagemaker_session = sagemaker.Session(
        boto_session=boto3.session.Session(region_name=djs.env.region)
    )
    s3_bucket_base_uri = "{}{}".format("s3://", sagemaker_session.default_bucket())
    output_data = "{}/{}".format(s3_bucket_base_uri, "data/sklearn_processing/output")

    input_data = f"s3://sagemaker-sample-data-{djs.env.region}/processing/census/census-income.csv"

    input_code = sagemaker_session.upload_data(
        "resources/preprocessing.py",
        bucket=sagemaker_session.default_bucket(),
        key_prefix="data/sklearn_processing/code",
    )

    inputs = [
        ProcessingInput(
            source=input_data,
            destination="/opt/ml/processing/input",
            input_name="input-1",
        ),
        ProcessingInput(
            source=input_code,
            destination="/opt/ml/processing/input/code",
            input_name="code",
        ),
    ]

    outputs = [
        ProcessingOutput(
            source="/opt/ml/processing/train",
            destination="{}/{}".format(output_data, "train_data"),
            output_name="train_data",
        ),
        ProcessingOutput(
            source="/opt/ml/processing/test",
            destination="{}/{}".format(output_data, "test_data"),
            output_name="test_data",
        ),
    ]

    processor = SKLearnProcessor(
        framework_version="0.20.0",
        role=role,
        instance_type="ml.m5.xlarge",
        instance_count=1,
    )

    processing_step = ProcessingStep(
        datajob_stack=djs,
        name="processing-job",
        processor=processor,
        inputs=inputs,
        outputs=outputs,
        container_arguments=["--train-test-split-ratio", "0.2"],
        container_entrypoint=[
            "python3",
            "/opt/ml/processing/input/code/preprocessing.py",
        ],
    )

    preprocessed_training_data = "{}/{}".format(output_data, "train_data")

    sklearn_image = sagemaker.image_uris.retrieve(
        framework="sklearn", region=djs.env.region, version="0.20.0", py_version="py3"
    )

    estimator = SKLearn(
        entry_point="resources/train.py",
        train_instance_type="ml.m5.xlarge",
        role=role,
        image_uri=sklearn_image,
        framework_version="0.20.0",
        py_version="py3",
    )

    training_step = TrainingStep(
        datajob_stack=djs,
        name="training-job",
        estimator=estimator,
        data={
            "train": sagemaker.TrainingInput(
                preprocessed_training_data, content_type="text/csv"
            )
        },
        wait_for_completion=True,
    )

    model_step = ModelStep(
        datajob_stack=djs,
        name="create-model",
        model=training_step.sfn_task.get_expected_model(),
    )

    with StepfunctionsWorkflow(djs, "workflow") as sfn_workflow:
        (processing_step >> training_step >> model_step)

app.synth()
