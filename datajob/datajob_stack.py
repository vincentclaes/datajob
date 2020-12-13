import os

from aws_cdk import core

from datajob import logger
from datajob.datajob_context import DatajobContext


class DataJobStack(core.Stack):
    def __init__(
        self,
        stack_name: str,
        stage: str = None,
        project_root: str = None,
        include_folder: str = None,
        account: str = None,
        region: str = None,
        scope: core.Construct = core.App(),
        **kwargs,
    ) -> None:
        """
        :param scope: aws cdk core construct object.
        :param stack_name: a name for this stack.
        :param stage: the stage name to which we are deploying
        :param project_root: the path to the root of this project
        :param include_folder:  specify the name of the folder we would like to include in the deployment bucket.
        :param account: AWS account number
        :param region: AWS region where we want to deploy our datajob to
        :param kwargs: any extra kwargs for the core.Construct
        """

        account = (
            account if account is not None else os.environ.get("AWS_DEFAULT_ACCOUNT")
        )
        region = region if region is not None else os.environ.get("AWS_DEFAULT_REGION")
        env = {"region": region, "account": account}
        self.scope = scope
        self.stage = stage if stage is not None else self.get_context_parameter("stage")
        self.unique_stack_name = self._create_unique_stack_name(stack_name, self.stage)
        super().__init__(scope=scope, id=self.unique_stack_name, env=env, **kwargs)
        self.project_root = project_root
        self.include_folder = include_folder
        self.resources = []
        self.datajob_context = None

    def __enter__(self):
        """
        As soon as we enter the contextmanager, we create the datajob context.
        :return: datajob stack.
        """
        self.datajob_context = DatajobContext(
            self,
            unique_stack_name=self.unique_stack_name,
            project_root=self.project_root,
            include_folder=self.include_folder,
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        steps we have to do when exiting the context manager.
        - we will create the resources we have defined.
        - we will synthesize our stack so that we have everything to deploy.
        :param exc_type:
        :param exc_value:
        :param traceback:
        :return: None
        """
        logger.debug("creating resources and synthesizing stack.")
        self.create_resources()
        self.scope.synth()

    def add(self, task: str) -> None:
        setattr(self, task.unique_name, task)
        task.create(datajob_context=self.datajob_context)

    @staticmethod
    def _create_unique_stack_name(stack_name: str, stage: str) -> str:
        """
        create a unique name for the datajob stack.
        :param stack_name: a name for the stack.
        :param stage: the stage name we give our pipeline.
        :return: a unique name.
        """
        return f"{stack_name}-{stage}"

    def create_resources(self):
        """create each of the resources of this stack"""
        [resource.create() for resource in self.resources]

    def get_context_parameter(self, name: str) -> str:
        """get a cdk context parameter from the cli."""
        context_parameter = self.scope.node.try_get_context(name)
        if not context_parameter:
            raise ValueError(
                "we expect a stage to be set on the cli. e.g 'cdk deploy -c stage=my-stage'"
            )
        logger.debug(f"context parameter {name} found.")
        return context_parameter
