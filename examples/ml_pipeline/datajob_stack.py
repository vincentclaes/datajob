import sagemaker
from aws_cdk import core
from sagemaker.processing import ProcessingInput
from sagemaker.processing import ProcessingOutput
from sagemaker.sklearn import SKLearnProcessor
from sagemaker.sklearn.estimator import SKLearn

from datajob.datajob_stack import DataJobStack
from datajob.sagemaker import ProcessingStep
from datajob.sagemaker import TrainingStep
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow

role = "arn:aws:iam::077590795309:role/service-role/AmazonSageMaker-ExecutionRole-20191008T190827"
app = core.App()

with DataJobStack(scope=app, id="datajob-ml-pipeline") as djs:
    PREPROCESSING_SCRIPT_LOCATION = "resources/preprocessing.py"

    sagemaker_session = sagemaker.Session()
    region = "eu-west-1"

    input_data = (
        "s3://sagemaker-sample-data-{}/processing/census/census-income.csv".format(
            region
        )
    )

    input_code = sagemaker_session.upload_data(
        PREPROCESSING_SCRIPT_LOCATION,
        bucket=sagemaker_session.default_bucket(),
        key_prefix="data/sklearn_processing/code",
    )

    s3_bucket_base_uri = "{}{}".format("s3://", sagemaker_session.default_bucket())
    output_data = "{}/{}".format(s3_bucket_base_uri, "data/sklearn_processing/output")
    preprocessed_training_data = "{}/{}".format(output_data, "train_data")

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
        framework_version="0.23-1",
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

    estimator = SKLearn(
        entry_point="resources/train.py",
        train_instance_type="ml.m5.xlarge",
        role=role,
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

    with StepfunctionsWorkflow(djs, "some-name") as sfn_workflow:
        processing_step >> training_step

app.synth()
