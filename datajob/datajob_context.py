from pathlib import Path

from aws_cdk import core, aws_s3_deployment, aws_s3
from aws_empty_bucket.empty_s3_bucket import EmptyS3Bucket

from datajob import logger


class DatajobContextError(Exception):
    """any exception occuring when constructing data job context."""


class DatajobContextWheelError(Exception):
    """any exception occuring when constructing wheel in data job context."""


class DatajobContext(core.Construct):
    """
    GlueJobContext is a class that creates all the services necessary for a glue job to run.
    You have to instantiate once and pass the instance to the different GlueJobs.
    """

    def __init__(
        self,
        scope: core.Construct,
        unique_stack_name: str,
        project_root: str = None,
        include_folder: str = None,
        **kwargs,
    ) -> None:
        """
        :param scope: aws cdk core construct object.
        :param unique_stack_name: a unique name for this stack. like this the name of our resources will not collide with other deployments.
        :param stage: the stage name to which we are deploying
        :param project_root: the path to the root of this project
        :param include_folder: specify the name of the folder we would like to include in the deployment bucket.
        :param kwargs: any extra kwargs for the core.Construct
        """
        logger.info("creating glue context.")
        super().__init__(scope, unique_stack_name, **kwargs)
        self.project_root = project_root
        self.unique_stack_name = unique_stack_name
        (
            self.deployment_bucket,
            self.deployment_bucket_name,
        ) = self._create_deployment_bucket(self.unique_stack_name)
        (
            self.data_bucket,
            self.data_bucket_name,
        ) = self._create_data_bucket(self.unique_stack_name)
        self.s3_url_wheel = None
        if self.project_root:
            self.s3_url_wheel = self._build_and_deploy_wheel(
                self.unique_stack_name,
                self.project_root,
                self.deployment_bucket,
                self.deployment_bucket_name,
            )

        if include_folder:
            self._deploy_local_folder(include_folder)
        logger.info("glue context created.")

    def _create_data_bucket(self, unique_stack_name):
        """use the unique stack name to create an s3 bucket for your data.
        We take an EmptyS3Bucket so that we can remove the stack including the deployment bucket with its contents.
        if we take a regular S3 bucket, the bucket will be orphaned from the stack leaving
        our account with all oprhaned s3 buckets."""
        data_bucket_name = f"{unique_stack_name}"
        # todo - can we validate the bucket name?
        logger.debug(f"creating deployment bucket {data_bucket_name}")
        data_bucket = EmptyS3Bucket(
            self,
            data_bucket_name,
            bucket_name=data_bucket_name,
            removal_policy=core.RemovalPolicy.DESTROY,
        )
        return data_bucket, data_bucket_name

    def _create_deployment_bucket(self, unique_stack_name):
        """use the unique stack name to create an s3 bucket for deployment purposes.
        We take an EmptyS3Bucket so that we can remove the stack including the deployment bucket with its contents.
        if we take a regular S3 bucket, the bucket will be orphaned from the stack leaving
        our account with all oprhaned s3 buckets."""
        deployment_bucket_name = f"{unique_stack_name}-deployment-bucket"
        # todo - can we validate the bucket name?
        logger.debug(f"creating deployment bucket {deployment_bucket_name}")
        deployment_bucket = EmptyS3Bucket(
            self,
            deployment_bucket_name,
            bucket_name=deployment_bucket_name,
            removal_policy=core.RemovalPolicy.DESTROY,
        )
        return deployment_bucket, deployment_bucket_name

    def _build_and_deploy_wheel(
        self,
        unique_stack_name: str,
        project_root: str,
        glue_deployment_bucket: aws_s3.Bucket,
        glue_deployment_bucket_name: str,
    ) -> str:
        """create a wheel and add the .whl file to the deployment bucket"""
        s3_url_wheel = None
        try:
            wheel_deployment_name = f"{unique_stack_name}-wheel"
            # todo - we should get this name dynamically
            logger.debug(f"deploying wheel {wheel_deployment_name}")
            aws_s3_deployment.BucketDeployment(
                self,
                wheel_deployment_name,
                sources=[
                    aws_s3_deployment.Source.asset(str(Path(project_root, "dist")))
                ],
                destination_bucket=glue_deployment_bucket,
                destination_key_prefix=wheel_deployment_name,
            )
            s3_url_wheel = self._get_wheel_name(
                glue_deployment_bucket_name, wheel_deployment_name, project_root
            )
            logger.debug(f"wheel will be located at {s3_url_wheel}")
        except DatajobContextWheelError as e:
            logger.warning("something went wrong while creating a wheel." f"{e}")
            s3_url_wheel = None
        finally:
            return s3_url_wheel

    def _get_wheel_name(
        self,
        glue_deployment_bucket_name,
        wheel_deployment_name,
        project_root,
        dist_folder="dist",
    ):
        dist_file_names = list(Path(project_root, dist_folder).glob("*.whl"))
        if len(dist_file_names) != 1:
            raise DatajobContextError(f"we expected 1 wheel: {dist_file_names}")
        # todo - improve creation of s3 urls
        return f"s3://{glue_deployment_bucket_name}/{wheel_deployment_name}/{dist_file_names[0].name}"

    def _deploy_local_folder(self, include_folder):
        """deploy a local folder from our project to the deployment bucket."""
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
