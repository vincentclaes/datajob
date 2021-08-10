from abc import abstractmethod

import stepfunctions.steps
from aws_cdk import aws_iam as iam
from aws_cdk import core

from datajob import logger
from datajob.datajob_stack import DataJobStack


class DataJobBase(core.Construct):
    def __init__(self, datajob_stack, name):
        super().__init__(datajob_stack, name)
        assert isinstance(
            datajob_stack, DataJobStack
        ), f"we expect the scope argument to be of type {DataJobStack}"
        self.datajob_stack = datajob_stack
        self.name = name
        self.project_root = self.datajob_stack.project_root
        self.stage = self.datajob_stack.stage
        self.unique_name = f"{self.datajob_stack.unique_stack_name}-{self.name}"
        self.context = self.datajob_stack.context
        self.datajob_stack.update_datajob_stack_resources(resource=self)
        self._sfn_task = None

    @property
    def sfn_task(self) -> stepfunctions.steps.Task:
        """This property function returns the stepfunctions Task instance of
        your service if it's implemented.

        If it's not implemented it throws an error.
        """
        if self._sfn_task is None:
            raise NotImplementedError(
                f"Implement the sfn_task variable to your class {self} so "
                "that stepfunctions can orchestrate it."
            )
        return self._sfn_task

    @sfn_task.setter
    def sfn_task(self, task: stepfunctions.steps.Task) -> None:
        """This setter function sets the sfn_task value to an instance of
        stepfunctions Task class. Setting self.sfn_task to an instance of Task
        in the constructor will call this function.

        Args:
            task: instance of a stepfunctions task

        Returns: None
        """
        self._sfn_task = task

    @abstractmethod
    def create(self):
        """create the resource using IAC techology like AWS CDK."""

    @staticmethod
    def get_default_admin_role(
        datajob_stack: DataJobStack, unique_name: str, service_principal: str
    ) -> iam.Role:
        """Get the default role with admin rights for the datajob. We use
        administrator access as the policy for our default role.

        Args:
            datajob_stack: stack construct for this role.
            unique_name: a unique name we can give to our role.
            service_principal: what is the service principal for our service.

        Returns: iam role object.
        """
        role_name = unique_name + "-default-role"
        logger.debug(f"creating role {role_name}")
        return iam.Role(
            datajob_stack,
            role_name,
            assumed_by=iam.ServicePrincipal(service_principal),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
            ],
        )

    @staticmethod
    def get_role(
        datajob_stack: DataJobStack,
        role: iam.Role,
        unique_name: str,
        service_principal: str,
    ) -> iam.Role:
        """If role is None, return a default one.

        :param unique_name: a unique name we can give to our role.
        :param service_principal: what is the service principal for our service.
        for example: glue.amazonaws.com
        :return: iam role object.
        """
        if role is None:
            logger.warning(
                "No role is provided, taking the default role with AdministratorAccess!"
            )
            return DataJobBase.get_default_admin_role(
                datajob_stack=datajob_stack,
                unique_name=unique_name,
                service_principal=service_principal,
            )
        return role

    def __repr__(self):
        return f"{self}"

    def __str__(self):
        return f"type: {type(self)} with name : {self.name}"
