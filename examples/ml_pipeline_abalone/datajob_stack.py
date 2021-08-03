"""https://github.com/aws/amazon-sagemaker-examples/blob/master/step-functions-
data-science-sdk/machine_learning_workflow_abalone/machine_learning_workflow_ab
alone.ipynb."""
import boto3
import sagemaker
from aws_cdk import core
from sagemaker import image_uris

from datajob.datajob_stack import DataJobStack
from datajob.glue.glue_job import GlueJob
from datajob.sagemaker import get_default_sagemaker_role
from datajob.sagemaker.sagemaker_job import EndpointConfigStep
from datajob.sagemaker.sagemaker_job import EndpointStep
from datajob.sagemaker.sagemaker_job import ModelStep
from datajob.sagemaker.sagemaker_job import TrainingStep
from datajob.stepfunctions.stepfunctions_workflow import StepfunctionsWorkflow

app = core.App()


with DataJobStack(scope=app, id="datajob-ml-pipeline-abalone") as djs:

    sagemaker_default_role = get_default_sagemaker_role(datajob_stack=djs)
    sagemaker_session = sagemaker.Session(
        boto_session=boto3.session.Session(region_name=djs.env.region)
    )
    sagemaker_default_bucket_uri = (
        f"s3://{sagemaker_session.default_bucket()}/datajob-ml-pipeline-abalone"
    )

    train_path = f"{sagemaker_default_bucket_uri}/train/abalone.train"
    validation_path = f"{sagemaker_default_bucket_uri}/validation/abalone.validation"
    test_path = f"{sagemaker_default_bucket_uri}/test/abalone.test"

    prepare_dataset_step = GlueJob(
        datajob_stack=djs,
        name="prepare-dataset",
        job_path="jobs/prepare_dataset.py",
        job_type="pythonshell",
        max_capacity=1,
        arguments={
            "--train": train_path,
            "--validation": validation_path,
            "--test": test_path,
        },
    )

    xgb = sagemaker.estimator.Estimator(
        image_uris.retrieve("xgboost", djs.env.region, "1.2-1"),
        role=sagemaker_default_role.role_arn,
        train_instance_count=1,
        train_instance_type="ml.m4.4xlarge",
        train_volume_size=5,
        output_path=f"{sagemaker_default_bucket_uri}/single-xgboost",
        sagemaker_session=sagemaker_session,
    )

    xgb.set_hyperparameters(
        objective="reg:linear",
        num_round=50,
        max_depth=5,
        eta=0.2,
        gamma=4,
        min_child_weight=6,
        subsample=0.7,
    )

    training_step = TrainingStep(
        datajob_stack=djs,
        name="train-model",
        estimator=xgb,
        data={
            "train": sagemaker.TrainingInput(train_path, content_type="text/libsvm"),
            "validation": sagemaker.TrainingInput(
                validation_path, content_type="text/libsvm"
            ),
        },
    )

    model_step = ModelStep(
        datajob_stack=djs,
        name="create-sagemaker-model",
        model=training_step.sfn_task.get_expected_model(),
    )

    endpoint_config_step = EndpointConfigStep(
        datajob_stack=djs,
        name="create-sagemaker-endpoint-config",
        model_name=model_step.model_name,
        initial_instance_count=1,
        instance_type="ml.m5.large",
    )

    endpoint_step = EndpointStep(
        datajob_stack=djs,
        name="create-endpoint",
        endpoint_config_name=endpoint_config_step.endpoint_config_name,
    )

    with StepfunctionsWorkflow(djs, "workflow") as sfn_workflow:
        (
            prepare_dataset_step
            >> training_step
            >> model_step
            >> endpoint_config_step
            >> endpoint_step
        )

app.synth()
