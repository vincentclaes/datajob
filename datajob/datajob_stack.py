from aws_cdk import core
from datajob.datajob_context import DatajobContext


class DataJobStack(core.Stack):
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
        self.scope = scope
        self.project_root = project_root
        self.stage = stage
        self.unique_stack_name = unique_stack_name
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