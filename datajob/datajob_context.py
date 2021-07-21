import uuid
from pathlib import Path

from aws_cdk import aws_s3
from aws_cdk import aws_s3_deployment
from aws_cdk import core
from aws_empty_bucket.empty_s3_bucket import EmptyS3Bucket

from datajob import logger


class DataJobContextError(Exception):
    """any exception occuring when constructing data job context."""


class DataJobContextWheelError(Exception):
    """any exception occuring when constructing wheel in data job context."""


class DataJobContext(core.Construct):
    """DataJobContext is a class that creates context in order to deploy and
    run our pipeline. You have to instantiate this class once per DatajobStack.

    DataJobContext creates:
        - data bucket: this is the bucket that you can use to ingest, dump intermediate results and the final ouptut.
        - deployment bucket: this is the bucket that holds you code ( scripts, wheel, config, ...)
    """

    def __init__(
        self,
        scope: core.Construct,
        project_root: str = None,
        include_folder: str = None,
        **kwargs,
    ) -> None:
        """
        :param scope: aws cdk core construct object.
        :param stage: stage from DataJobStack.
        :param project_root: the path to the root of this project
        :param include_folder: specify the name of the folder we would like to include in the deployment bucket.
        """
        logger.info("creating datajob context.")
        self.unique_stack_name = scope.unique_stack_name
        super().__init__(scope, self.unique_stack_name, **kwargs)
        self.stage = scope.stage
        self.bucket_suffix = None
        self.project_root = project_root
        (
            self.deployment_bucket,
            self.deployment_bucket_name,
        ) = self._create_deployment_bucket()
        (self.data_bucket, self.data_bucket_name) = self._create_data_bucket()
        self.s3_url_wheel = None
        if self.project_root:
            self.s3_url_wheel = self._deploy_wheel(
                self.unique_stack_name,
                self.project_root,
                self.deployment_bucket,
                self.deployment_bucket_name,
            )

        if include_folder:
            self._deploy_local_folder(include_folder)
        logger.info("datajob context created.")

    def _create_data_bucket(self) -> tuple:
        """use the unique stack name to create an s3 bucket for your data. We
        take an EmptyS3Bucket so that we can remove the stack including the
        deployment bucket with its contents. if we take a regular S3 bucket,
        the bucket will be orphaned from the stack leaving our account with all
        oprhaned s3 buckets.

        :param unique_stack_name: the unique stack name of the datajob stack.
        :return: s3 bucket object, name of our bucket
        """
        data_bucket_name = self._get_unique_bucket_name()
        # todo - can we validate the bucket name?
        logger.debug(f"creating deployment bucket {data_bucket_name}")
        data_bucket = EmptyS3Bucket(
            self,
            data_bucket_name,
            bucket_name=data_bucket_name,
            # todo - we might want to refine the removal policy.
            #  Might not be wise to destroy it after we destroy the stack.
            removal_policy=core.RemovalPolicy.DESTROY,
        )
        return data_bucket, data_bucket_name

    def _create_deployment_bucket(self) -> tuple:
        """use the unique stack name to create an s3 bucket for deployment
        purposes. We take an EmptyS3Bucket so that we can remove the stack
        including the deployment bucket with its contents. if we take a regular
        S3 bucket, the bucket will be orphaned from the stack leaving our
        account with all oprhaned s3 buckets.

        :param unique_stack_name: the unique stack name of the datajob stack.
        :return: s3 bucket object, name of our bucket
        """
        unique_bucket_name = self._get_unique_bucket_name()
        deployment_bucket_name = f"{unique_bucket_name}-deployment-bucket"
        # todo - can we validate the bucket name?
        logger.debug(f"creating deployment bucket {deployment_bucket_name}")
        deployment_bucket = EmptyS3Bucket(
            self,
            deployment_bucket_name,
            bucket_name=deployment_bucket_name,
            removal_policy=core.RemovalPolicy.DESTROY,
        )
        return deployment_bucket, deployment_bucket_name

    def _get_unique_bucket_name(self):
        """if a stage is specified we use the unique_stack_name, if no stage is
        specified we return some random characters to have a high chance of a
        unique name."""
        if self.stage:
            logger.debug(
                "We have a stage therefore we have a unique name for our bucket."
            )
            return self.unique_stack_name
        logger.debug(
            "We don't have a stage, therefore we generate a random value for the bucketname."
        )
        return f"{self.unique_stack_name}-{uuid.uuid4().hex[:4]}"

    def _deploy_wheel(
        self,
        unique_stack_name: str,
        project_root: str,
        deployment_bucket: aws_s3.Bucket,
        deployment_bucket_name: str,
    ) -> str:
        """Create a wheel and add the .whl file to the deployment bucket.

        :param unique_stack_name: the unique stack name of the datajob stack.
        :param project_root: the absolute path to the root of a project.
        :param deployment_bucket: s3 deployment bucket object
        :param deployment_bucket_name:  s3 deployment bucket name
        :return: s3 url to the wheel we deployed onto the deployment bucket.
        """
        s3_url_wheel = None
        try:
            wheel_deployment_name = f"{unique_stack_name}-wheel"
            logger.debug(f"deploying wheel {wheel_deployment_name}")
            aws_s3_deployment.BucketDeployment(
                self,
                wheel_deployment_name,
                sources=[
                    aws_s3_deployment.Source.asset(str(Path(project_root, "dist")))
                ],
                destination_bucket=deployment_bucket,
                destination_key_prefix=wheel_deployment_name,
            )
            s3_url_wheel = self._get_wheel_name(
                deployment_bucket_name, wheel_deployment_name, project_root
            )
            logger.debug(f"wheel will be located at {s3_url_wheel}")
        except DataJobContextWheelError as e:
            logger.warning("something went wrong while creating a wheel." f"{e}")
            s3_url_wheel = None
        finally:
            return s3_url_wheel

    @staticmethod
    def _get_wheel_name(
        deployment_bucket_name: str,
        wheel_deployment_name: str,
        project_root: str,
        dist_folder="dist",
    ):
        """find the name of the wheel we created.

        :param deployment_bucket_name:  s3 deployment bucket name.
        :param wheel_deployment_name: name of the wheel of our project.
        :param project_root: the absolute path to the root of a project.
        :param dist_folder: the folder where our whl resides. typically this is dist/
        :return: s3 url to the wheel we deployed onto the deployment bucket.
        """
        dist_file_names = list(Path(project_root, dist_folder).glob("*.whl"))
        if len(dist_file_names) != 1:
            raise DataJobContextError(f"we expected 1 wheel: {dist_file_names}")
        # todo - improve creation of s3 urls
        return f"s3://{deployment_bucket_name}/{wheel_deployment_name}/{dist_file_names[0].name}"

    def _deploy_local_folder(self, include_folder: str) -> None:
        """deploy the contents of a local folder from our project to the
        deployment bucket.

        :param include_folder: path to the folder
        :return: None
        """
        logger.debug(f"deploying local folder {include_folder}")
        folder_deployment = f"{self.unique_stack_name}-FolderDeployment"
        aws_s3_deployment.BucketDeployment(
            self,
            folder_deployment,
            sources=[
                aws_s3_deployment.Source.asset(
                    str(Path(self.project_root, include_folder))
                )
            ],
            destination_bucket=self.deployment_bucket,
            destination_key_prefix=include_folder,
        )
