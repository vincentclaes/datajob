from pathlib import Path

from aws_cdk import core

from datajob import ROOT_DIR
from datajob.datajob_context import DatajobContext
from datajob.glue.glue_job import GlueJob


class TechSkillsParserStack(core.Stack):
    """
    Stack definition of all the resources needed for tech_skills_parser.
    We define a GlueJobContext once to create all the necessary
    services to create and deploy a GlueJob.
    """

    def __init__(
        self,
        scope: core.Construct,
        unique_stack_name: str,
        stage: str,
        project_root: str,
        include_folder: str = None,
        **kwargs,
    ) -> None:
        """

        :param scope: aws cdk core construct object.
        :param unique_stack_name: a unique name for this stack. like this the name of our resources will not collide with other deployments.
        :param stage: the stage name to which we are deploying
        :param project_root: the path to the root of this project
        :param include_folder:  specify the name of the folder we would like to include in the deployment bucket.
        :param kwargs: any extra kwargs for the core.Construct
        """
        super().__init__(scope=scope, id=unique_stack_name, **kwargs)
        self.project_root = project_root
        self.stage = stage
        self.unique_stack_name = unique_stack_name
        self.glue_job_context = DatajobContext(
            self,
            unique_stack_name=self.unique_stack_name,
            project_root=self.project_root,
            include_folder=include_folder,
        )
        self.glue_job_keywords_cleaning = GlueJob(
            self,
            "KeywordsCleaning",
            glue_job_context=self.glue_job_context,
            stage=self.stage,
            path_to_glue_job=str(Path(ROOT_DIR, "glue/jobs/keywords_cleaning.py")),
            job_type="pythonshell",
            glue_version="1.0",
            max_capacity=1,
            python_version="3",
            arguments={
                "--input_file": f"s3://{self.glue_job_context.glue_deployment_bucket_name}/tech_skills_parser/assets/raw_skills_keywords.csv",
                "--output_file": f"s3://{self.glue_job_context.glue_deployment_bucket_name}/tech_skills_parser/assets/cleaned_skills_keywords.csv",
            },
        )

        self.glue_job_vacancy_cleaning = GlueJob(
            self,
            "VacancyCleaning",
            glue_job_context=self.glue_job_context,
            stage=self.stage,
            path_to_glue_job=str(Path(ROOT_DIR, "glue/jobs/vacancy_cleaning.py")),
            job_type="pythonshell",
            glue_version="1.0",
            max_capacity=1,
            python_version="3",
            arguments={
                "--source": "indeed_jobs.sample_ny_data",
                "--destination": "indeed_jobs.sample_ny_data__vacancy_cleaning",
                "--columns": "job_description",
            },
        )

        self.glue_job_create_tf_matrix = GlueJob(
            self,
            "CreateTfMatrix",
            glue_job_context=self.glue_job_context,
            stage=self.stage,
            path_to_glue_job=str(Path(ROOT_DIR, "glue/jobs/create_tf_matrix.py")),
            job_type="pythonshell",
            glue_version="1.0",
            max_capacity=1,
            python_version="3",
            arguments={
                "--source": "indeed_jobs.sample_ny_data__vacancy_cleaning",
                "--destination": "indeed_jobs.sample_ny_data__create_tf_matrix",
                "--columns": "job_description",
            },
        )
