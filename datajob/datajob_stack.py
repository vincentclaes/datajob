import os
from typing import Union

from aws_cdk import core
from aws_cdk.core import CfnOutput

from datajob import logger
from datajob.datajob_context import DataJobContext
from datajob.datajob_execution_input import DataJobExecutionInput


class DataJobStack(core.Stack):
    STAGE_NAME = "stage"

    def __init__(
        self,
        scope: core.Construct,
        id: str,
        stage: str = None,
        project_root: str = None,
        include_folder: str = None,
        account: str = None,
        region: str = None,
        **kwargs,
    ) -> None:
        """
        :param scope: aws cdk core construct object.
        :param id: a name for this stack.
        :param stage: the stage name to which we are deploying
        :param project_root: the path to the root of this project
        :param include_folder:  specify the path to the folder we would like to include in the deployment bucket.
        :param account: AWS account number
        :param region: AWS region where we want to deploy our datajob to
        :param kwargs: any extra kwargs for the core.Construct
        """
        self.scope = scope
        self.env = DataJobStack._create_environment_object(
            account=account, region=region
        )
        self.stage = self.get_stage(stage)
        self.unique_stack_name = self._create_unique_stack_name(id, self.stage)
        super().__init__(scope=scope, id=self.unique_stack_name, env=self.env, **kwargs)
        self.project_root = project_root
        self.include_folder = include_folder
        self.resources = []
        self.outputs = {}
        self.execution_input = DataJobExecutionInput()
        self.context = None

    def __enter__(self):
        """As soon as we enter the contextmanager, we create the datajob
        context.

        :return: datajob stack.
        """
        self.init_datajob_context()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """steps we have to do when exiting the context manager. We execute the
        steps when no exception is present.

        - we will create the resources we have defined.
        - we will create cloudformation stack outputs, if present.

        :param exc_type:
        :param exc_value:
        :param traceback:
        :return: None
        """
        if exc_type is None and exc_value is None and traceback is None:
            logger.debug("creating resources and synthesizing stack.")
            self.create_resources()

    def add(self, task: str) -> None:
        setattr(self, task.unique_name, task)
        task.create()

    def update_datajob_stack_outputs(self, key: str, value: str) -> None:
        """Add a key and value to datajob_stack output variable
        Returns:  None

        """
        self.outputs[key] = value

    def update_datajob_stack_resources(self, resource: object) -> None:
        """add  a DataJob resource to the DataJob stack resources variable.

        Args:
            resource: A DataJobBase implementation. we cannot reference it here explicitly
            in the typing, because then we  have a circular dependency conflict.

        Returns: None
        """
        logger.info(f"adding job {self} to stack workflow resources")
        self.resources.append(resource)

    @staticmethod
    def _create_unique_stack_name(stack_name: str, stage: Union[str, None]) -> str:
        """create a unique name for the datajob stack.

        :param stack_name: a name for the stack.
        :param stage: the stage name we give our pipeline.
        :return: a unique name.
        """
        if stage:
            return f"{stack_name}-{stage}"
        return stack_name

    @staticmethod
    def _create_environment_object(account: str, region: str) -> core.Environment:
        """create an aws cdk Environment object.

        Args:
            account: AWS account number: 12 numbers
            region: AWS region. e.g. eu-west-1

        Returns: AWS cdk Environment object.
        """
        account = (
            account if account is not None else os.environ.get("AWS_DEFAULT_ACCOUNT")
        )
        region = region if region is not None else os.environ.get("AWS_DEFAULT_REGION")
        return core.Environment(account=account, region=region)

    def create_cloudformation_outputs(self) -> None:
        """if the outputs dictionary has key value pairs, create these for the
        cloudformation stack outputs.

        Returns:  None
        """
        if self.outputs:
            for key, value in self.outputs.items():
                logger.debug(f"adding key {key} and value {value} to the stack output.")
                CfnOutput(scope=self, id=key, value=value)

    def create_resources(self) -> None:
        """create each of the resources of this stack."""
        if self.resources:
            for resource in self.resources:
                logger.debug(f"creating resource: {resource.name}")
                resource.create()
        logger.debug("no resources available to create.")

    def get_stage(self, stage: str) -> Union[str, None]:
        """get the stage parameter and return a default if not found."""
        if stage:
            logger.debug(
                "a stage parameter is passed directly to the stack object, take this value."
            )
            return stage
        else:
            logger.debug("check cdk context if there is not a stage value provided.")
            try:
                return self.get_context_parameter(DataJobStack.STAGE_NAME)
            except ValueError:
                logger.debug("no stage is found on the context. Will return None.")
                return None

    def get_context_parameter(self, name: str) -> str:
        """get a cdk context parameter from the cli."""
        context_parameter = self.scope.node.try_get_context(name)
        if not context_parameter:
            raise ValueError(
                f"we expect a cdk context parameter to be set on the cli with key {name}. "
                f"e.g 'cdk deploy -c stage=my-stage' where stage is the key and my-stage is the value."
            )
        logger.debug(f"context parameter {name} found.")
        return context_parameter

    def init_datajob_context(self) -> None:
        """Initializes a datajob context."""
        self.context = DataJobContext(
            self, project_root=self.project_root, include_folder=self.include_folder
        )
