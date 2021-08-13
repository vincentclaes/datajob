import os
import uuid
from collections import defaultdict
from typing import Iterator
from typing import Union

import boto3
import contextvars
import toposort
from aws_cdk import aws_iam as iam
from aws_cdk import core
from aws_cdk.aws_stepfunctions import CfnStateMachine
from stepfunctions.steps import Catch
from stepfunctions.steps import Chain
from stepfunctions.steps.compute import GlueStartJobRunStep
from stepfunctions.steps.service import SnsPublishStep
from stepfunctions.steps.states import Parallel
from stepfunctions.workflow import Workflow

from datajob import logger
from datajob.datajob_base import DataJobBase
from datajob.sns.sns import SnsTopic

__workflow = contextvars.ContextVar("workflow")


class StepfunctionsWorkflowException(Exception):
    pass


class StepfunctionsWorkflow(DataJobBase):
    """Class that defines the methods to create and execute an orchestration
    using the step functions sdk.

    example:

        with StepfunctionsWorkflow("techskills-parser") as tech_skills_parser_orchestration:

            some-glue-job-1 >> [some-glue-job-2,some-glue-job-3] >> some-glue-job-4

        tech_skills_parser_orchestration.execute()
    """

    def __init__(
        self,
        datajob_stack: core.Construct,
        name: str,
        notification: Union[str, list] = None,
        role: iam.Role = None,
        region: str = None,
        **kwargs,
    ):
        super().__init__(datajob_stack, name, **kwargs)
        self.workflow = None
        self.chain_of_tasks = None
        self.role = self.get_role(
            role=role,
            datajob_stack=datajob_stack,
            unique_name=self.unique_name,
            service_principal="states.amazonaws.com",
        )
        self.region = (
            region if region is not None else os.environ.get("AWS_DEFAULT_REGION")
        )
        self.notification = self._setup_notification(notification)
        self.kwargs = kwargs
        # init directed graph dict where values are a set.
        # we do it like this so that we can use toposort.
        self.directed_graph = defaultdict(set)

    def add_task(self, some_task: DataJobBase) -> object:
        """get the stepfunctions  task,  sfn_task, we would like to
        orchestrate."""
        return some_task.sfn_task

    def add_parallel_tasks(self, parallel_tasks: Iterator[DataJobBase]) -> Parallel:
        """add tasks in parallel (wrapped in a list) to the workflow we would
        like to orchestrate."""
        parallel_pipelines = Parallel(state_id=uuid.uuid4().hex)
        for a_task in parallel_tasks:
            logger.debug(f"adding parallel task {a_task}")
            sfn_task = self.add_task(a_task)
            parallel_pipelines.add_branch(sfn_task)
        return parallel_pipelines

    def _is_one_task(self, directed_graph_toposorted):
        """If we have length of 2 and the second is an Ellipsis object we have
        scheduled 1 task.

        example:
            some_task >> ...

        :param directed_graph_toposorted: a toposorted graph, a graph with all the sorted tasks
        :return: boolean
        """
        return len(directed_graph_toposorted) == 2 and isinstance(
            list(directed_graph_toposorted[1])[0], type(Ellipsis)
        )

    def _construct_toposorted_chain_of_tasks(self) -> Chain:
        """Take the directed graph and toposort so that we can efficiently
        organize our workflow, i.e. parallelize where possible.

        if we have 2 elements where one of both is an Ellipsis object we need to orchestrate just 1 job.
        In the other case we will loop over the toposorted dag and assign a stepfunctions task
        or assign multiple tasks in parallel.

        Returns: toposorted chain of tasks
        """
        self.chain_of_tasks = Chain()
        directed_graph_toposorted = list(toposort.toposort(self.directed_graph))
        if self._is_one_task(directed_graph_toposorted=directed_graph_toposorted):
            sfn_task = self.add_task(next(iter(directed_graph_toposorted[0])))
            self.chain_of_tasks.append(sfn_task)
        else:
            for element in directed_graph_toposorted:
                if len(element) == 1:
                    sfn_task = self.add_task(next(iter(element)))
                elif len(element) > 1:
                    sfn_task = self.add_parallel_tasks(element)
                else:
                    raise StepfunctionsWorkflowException(
                        "cannot have an index in the directed graph with 0 elements"
                    )
                self.chain_of_tasks.append(sfn_task)
        return self.chain_of_tasks

    def build_workflow(self):
        """create a step functions workflow from the chain_of_tasks."""
        self.chain_of_tasks = self._construct_toposorted_chain_of_tasks()
        logger.debug("creating a chain from all the different steps.")
        self.chain_of_tasks = self._integrate_notification_in_workflow(
            chain_of_tasks=self.chain_of_tasks
        )
        logger.debug(f"creating a workflow with name {self.unique_name}")
        sfn_client = boto3.client("stepfunctions")
        self.workflow = Workflow(
            name=self.unique_name,
            definition=self.chain_of_tasks,
            role=self.role.role_arn,
            client=sfn_client,
            **self.kwargs,
        )

    def create(self):
        """create sfn stack."""
        import json

        cfn_template = json.dumps(self.workflow.definition.to_dict())
        CfnStateMachine(
            scope=self.datajob_stack,
            id=self.unique_name,
            state_machine_name=self.unique_name,
            role_arn=self.role.role_arn,
            definition_string=cfn_template,
            **self.kwargs,
        )

    def _setup_notification(
        self, notification: Union[str, list]
    ) -> Union[SnsTopic, None]:
        """Create a SnsTopic if the notification parameter is defined.

        :param notification: email address as string or list of email addresses to be subscribed.
        :return:
        """
        if notification is not None:
            name = f"{self.name}-notification"
            return SnsTopic(self.datajob_stack, name, notification)

    def _integrate_notification_in_workflow(self, chain_of_tasks: Chain) -> Chain:
        """If a notification is defined we configure an SNS with email
        subscription to alert the user if the stepfunctions workflow failed or
        succeeded.

        :param chain_of_tasks: the workflow definition that contains all the steps we want to execute.
        :return: if notification is set, we adapt the workflow to include an SnsPublishStep on failure or on success.
        If notification is not set, we return the workflow as we received it.
        """
        if self.notification:
            logger.debug(
                "A notification is configured, "
                "implementing a notification on Error or when the stepfunctions workflow succeeds."
            )
            failure_notification = SnsPublishStep(
                "FailureNotification",
                parameters={
                    "TopicArn": self.notification.get_topic_arn(),
                    "Message": f"Stepfunctions workflow {self.unique_name} Failed.",
                },
            )
            pass_notification = SnsPublishStep(
                "SuccessNotification",
                parameters={
                    "TopicArn": self.notification.get_topic_arn(),
                    "Message": f"Stepfunctions workflow {self.unique_name} Succeeded.",
                },
            )

            catch_error = Catch(
                error_equals=["States.ALL"], next_step=failure_notification
            )
            workflow_with_notification = Parallel(state_id="notification")
            workflow_with_notification.add_branch(chain_of_tasks)
            workflow_with_notification.add_catch(catch_error)
            workflow_with_notification.next(pass_notification)
            return Chain([workflow_with_notification])
        logger.debug(
            "No notification is configured, returning the workflow definition."
        )
        return chain_of_tasks

    def __enter__(self):
        """first steps we have to do when entering the context manager."""
        logger.info(f"creating step functions workflow for {self.unique_name}")
        _set_workflow(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """steps we have to do when exiting the context manager."""
        self.build_workflow()
        _set_workflow(None)
        logger.info(f"step functions workflow {self.unique_name} created")


def task(self):
    """Task that can configured in the orchestration of a
    StepfunctionsWorkflow. You have to use this as a decorator for any class
    that you want to use in the orchestration.

    example:

        @stepfunctions.task
        class GlueJob(core.Construct):
            pass

    once this decorator is added to a class, for example GlueJob, the functions of task are inherited
    so that we can use >> to configure the orchestration.

    glue_job_1 = GlueJob()
    glue_job_2 = GlueJob()

    glue_job_1 >>  glue_job_2
    """

    def __rshift__(
        self: DataJobBase, other: DataJobBase, *args, **kwargs
    ) -> DataJobBase:
        """called when doing task1 >> task2.

        Syntactic suggar for >>.
        """
        connect(self=self, other=other)
        return other

    setattr(self, "__rshift__", __rshift__)
    return self


def _set_workflow(workflow: Workflow):
    __workflow.set(workflow)


def _get_workflow():
    try:
        return __workflow.get()
    except LookupError:
        return None


def connect(self, other: DataJobBase) -> None:
    work_flow = _get_workflow()
    work_flow.directed_graph[other].add(self)
