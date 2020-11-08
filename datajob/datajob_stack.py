from aws_cdk import core
import os
from datajob.datajob_context import DatajobContext


class DataJobStack(core.Stack):
    def __init__(
        self,
        stack_name: str,
        stage: str,
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
        :param kwargs: any extra kwargs for the core.Construct
        """

        account = (
            account if account is not None else os.environ.get("AWS_DEFAULT_ACCOUNT")
        )
        region = region if region is not None else os.environ.get("AWS_DEFAULT_REGION")
        env = {"region": region, "account": account}
        self.stage = stage
        self.unique_stack_name = self._create_unique_stack_name(stack_name, self.stage)
        super().__init__(scope=scope, id=self.unique_stack_name, env=env, **kwargs)
        self.scope = scope
        self.project_root = project_root
        self.include_folder = include_folder
        self.resources = []
        self.datajob_context = None

    def __enter__(self):
        """first steps we have to do when entering the context manager."""
        self.datajob_context = DatajobContext(
            self,
            unique_stack_name=self.unique_stack_name,
            project_root=self.project_root,
            include_folder=self.include_folder,
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """steps we have to do when exiting the context manager."""
        self.scope.synth()

    def add(self, task):
        setattr(self, task.unique_name, task)
        task.deploy(datajob_context=self.datajob_context)

    @staticmethod
    def _create_unique_stack_name(stack_name, stage):
        return f"{stack_name}-{stage}"
