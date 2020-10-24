from pathlib import Path

from aws_cdk import aws_glue as glue, core, aws_s3_deployment

from datajob import logger
from datajob.glue_job_context import GlueJobContext
from datajob import stepfunctions_workflow


@stepfunctions_workflow.task
class GlueJob(core.Construct):
    """
    Configure a glue job to run some business logic.
    """

    def __init__(
        self,
        scope: core.Construct,
        glue_job_name: str,
        glue_job_context: GlueJobContext,
        stage: str,
        path_to_glue_job: str,
        job_type: str,
        glue_version: str,
        max_capacity: int,
        arguments: dict,
        python_version: str = "3",
        *args,
        **kwargs,
    ):
        """
        :param scope: aws cdk core construct object.
        :param glue_job_name: a name for this glue job (will appear on the glue console).
        :param glue_job_context: context object that is created for the stack where this job is part of.
        :param stage: the stage name to which we are deploying
        :param path_to_glue_job: the path to the glue job relative to the project root.
        :param job_type: choose pythonshell for plain python / glueetl for a spark cluster.
        :param glue_version: at the time of writing choose 1.0 for pythonshell / 2.0 for spark.
        :param max_capacity: max nodes we want to run.
        :param arguments: the arguments as a dict for this glue job.
        :param python_version: 3 is the default
        :param args: any extra args for the glue.CfnJob
        :param kwargs: any extra kwargs for the glue.CfnJob
        """
        logger.info(f"creating glue job {glue_job_name}")
        super().__init__(scope, glue_job_name, **kwargs)
        self.unique_glue_job_name = f"{glue_job_name}-{stage}"
        s3_url_glue_job = self._deploy_glue_job_code(
            glue_job_context=glue_job_context,
            glue_job_name=self.unique_glue_job_name,
            path_to_glue_job=path_to_glue_job,
        )
        self._create_glue_job(
            glue_job_context=glue_job_context,
            glue_job_name=self.unique_glue_job_name,
            s3_url_glue_job=s3_url_glue_job,
            arguments=arguments,
            job_type=job_type,
            python_version=python_version,
            glue_version=glue_version,
            max_capacity=max_capacity,
            *args,
            **kwargs,
        )
        logger.info(f"glue job {glue_job_name} created.")

    @staticmethod
    def _create_s3_url_for_job(
        glue_job_context: GlueJobContext, glue_job_id: str, glue_job_file_name: str
    ):
        """path to the script on s3 for this job."""
        s3_url_glue_job = f"s3://{glue_job_context.glue_deployment_bucket_name}/{glue_job_id}/{glue_job_file_name}"
        logger.debug(f"s3 url for glue job {glue_job_id}: {s3_url_glue_job}")
        return s3_url_glue_job

    @staticmethod
    def _get_glue_job_dir_and_file_name(path_to_glue_job: str):
        """Split the full path in a dir and filename."""
        logger.debug(f"splitting path {path_to_glue_job}")
        pathlib_path_to_glue_job = Path(path_to_glue_job)
        glue_job_dir = str(pathlib_path_to_glue_job.parent)
        glue_job_file_name = pathlib_path_to_glue_job.name
        logger.debug(f"splitted into {glue_job_dir} and {glue_job_file_name}")
        return glue_job_dir, glue_job_file_name

    def _deploy_glue_job_code(
        self,
        glue_job_context: GlueJobContext,
        glue_job_name: str,
        path_to_glue_job: str,
    ):
        """deploy the code of this glue job to the deployment bucket (can be found in the glue context object)"""
        glue_job_dir, glue_job_file_name = GlueJob._get_glue_job_dir_and_file_name(
            path_to_glue_job=path_to_glue_job
        )
        logger.debug(f"deploying glue job folder {glue_job_dir}")
        aws_s3_deployment.BucketDeployment(
            self,
            f"{glue_job_name}-CodeDeploy",
            sources=[
                # we can either sync dirs or zip files.
                # To keep it easy for now we agreed to sync the full dir.
                # todo - sync only the glue job itself.
                aws_s3_deployment.Source.asset(glue_job_dir)
            ],
            destination_bucket=glue_job_context.glue_deployment_bucket,
            destination_key_prefix=glue_job_name,
        )

        s3_url_glue_job = GlueJob._create_s3_url_for_job(
            glue_job_context=glue_job_context,
            glue_job_id=glue_job_name,
            glue_job_file_name=glue_job_file_name,
        )
        return s3_url_glue_job

    def _create_glue_job(
        self,
        glue_job_context: GlueJobContext,
        glue_job_name: str,
        s3_url_glue_job: str,
        arguments: dict,
        job_type: str,
        python_version: str,
        glue_version: str,
        max_capacity: int,
        *args,
        **kwargs,
    ):
        """Create a glue job with the necessary configuration like, paths to wheel and business logic and arguments"""
        logger.debug(f"creating Glue Job {glue_job_name}")
        extra_py_files = {
            # path to the wheel of this project
            "--extra-py-files": glue_job_context.s3_url_wheel
        }
        default_arguments = {**extra_py_files, **arguments}
        glue.CfnJob(
            self,
            id=glue_job_name,
            name=glue_job_name,
            role=glue_job_context.glue_job_role.role_arn,
            command=glue.CfnJob.JobCommandProperty(
                name=job_type,
                python_version=python_version,
                script_location=s3_url_glue_job,
            ),
            glue_version=glue_version,
            max_capacity=max_capacity,
            default_arguments=default_arguments,
            *args,
            **kwargs,
        )
