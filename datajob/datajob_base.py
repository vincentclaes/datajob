from abc import abstractmethod

from aws_cdk import aws_iam as iam
from aws_cdk import core

from datajob import logger
from datajob.datajob_stack import DataJobStack


class DataJobBase(core.Construct):
    def __init__(self, datajob_stack, name, **kwargs):
        super().__init__(datajob_stack, name, **kwargs)
        assert isinstance(
            datajob_stack, DataJobStack
        ), f"we expect the scope argument to be of type {DataJobStack}"
        self.datajob_stack = datajob_stack
        self.name = name
        self.project_root = self.datajob_stack.project_root
        self.stage = self.datajob_stack.stage
        self.unique_name = f"{self.datajob_stack.unique_stack_name}-{self.name}"
        self.context = self.datajob_stack.context
        logger.info(f"adding job {self} to stack workflow resources")
        self.datajob_stack.resources.append(self)

    @abstractmethod
    def create(self):
        """create datajob"""

    def get_role(self, unique_name: str, service_principal: str) -> iam.Role:
        """
        Get the default role for the datajob. We use administrator access
        as the policy for our default role.
        # todo - we probably want to refine the policies for this role
        :param unique_name: a unique name we can give to our role.
        :param service_principal: what is the service principal for our service.
        for example: glue.amazonaws.com
        :return: iam role object.
        """
        role_name = unique_name + "-role"
        logger.debug(f"creating role {role_name}")
        return iam.Role(
            self,
            role_name,
            assumed_by=iam.ServicePrincipal(service_principal),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
            ],
        )
