import contextvars
import uuid

from stepfunctions import steps
from stepfunctions.steps.compute import GlueStartJobRunStep
from stepfunctions.steps.states import Parallel
from stepfunctions.workflow import Workflow

from datajob import logger

__workflow = contextvars.ContextVar("workflow")


class StepfunctionsWorkflow(object):
    """Class that defines the methods to create and execute an orchestration using the step functions sdk.

    example:

        with StepfunctionsWorkflow("techskills-parser", "arn:aws:iam:::role/some-role") as tech_skills_parser_orchestration:

            some-glue_job_include_packaged_project-job-1 >> [some-glue_job_include_packaged_project-job-2,some-glue_job_include_packaged_project-job-3] >> some-glue_job_include_packaged_project-job-4

        tech_skills_parser_orchestration.execute()

    """

    def __init__(self, unique_stack_name, role_arn):
        self.unique_stack_name = unique_stack_name
        self.role_arn = role_arn
        self.chain_of_tasks = []
        self.workflow = None

    def add_task(self, task_other):
        """add a task to the workflow we would like to orchestrate."""
        job_name = task_other.unique_name
        logger.debug(f"adding task with name {job_name}")
        task = StepfunctionsWorkflow._create_glue_start_job_run_step(job_name=job_name)
        self.chain_of_tasks.append(task)

    def add_parallel_tasks(self, task_others):
        """add tasks in parallel (wrapped in a list) to the workflow we would like to orchestrate."""
        deploy_pipelines = Parallel(state_id=uuid.uuid4().hex)
        for one_other_task in task_others:
            task_unique_name = one_other_task.unique_name
            logger.debug(f"adding parallel task with name {task_unique_name}")
            deploy_pipelines.add_branch(
                StepfunctionsWorkflow._create_glue_start_job_run_step(
                    job_name=task_unique_name
                )
            )
        self.chain_of_tasks.append(deploy_pipelines)

    @staticmethod
    def _create_glue_start_job_run_step(job_name):
        logger.debug("creating a step for a glue_job_include_packaged_project job.")
        return GlueStartJobRunStep(
            job_name,
            wait_for_completion=True,
            parameters={"JobName": job_name},
        )

    def _build_workflow(self):
        """create a step functions workflow from the chain_of_tasks."""
        logger.debug(
            f"creating a chain from all the different steps. \n {self.chain_of_tasks}"
        )
        workflow_definition = steps.Chain(self.chain_of_tasks)
        logger.debug(f"creating a workflow with name {self.unique_stack_name}")
        self.workflow = Workflow(
            name=self.unique_stack_name + "-" + uuid.uuid4().hex,
            definition=workflow_definition,
            role=self.role_arn,
        )
        self.workflow.create()

    def __enter__(self):
        """first steps we have to do when entering the context manager."""
        logger.info(f"creating step functions workflow for {self.unique_stack_name}")
        _set_workflow(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """steps we have to do when exiting the context manager."""
        self._build_workflow()
        _set_workflow(None)
        logger.info(f"step functions workflow {self.unique_stack_name} created")


def task(self):
    """
    Task that can configured in the orchestration of a StepfunctionsWorkflow.
    You have to use this as a decorator for any class that you want to use in the orchestration.

    example:

        @stepfunctions_workflow.task
        class GlueJob(core.Construct):
            pass

    once this decorator is added to a class, for example GlueJob, the functions of task are inherited
    so that we can use >> to configure the orchestration.

    glue_job_1 = GlueJob()
    glue_job_2 = GlueJob()

    glue_job_1 >>  glue_job_2
    """

    def __rshift__(self, other, *args, **kwargs):
        """called when doing
        - task1 >> task2
        - task1 >> [task2,task3]
        """
        _handle_first(self=self)
        _connect(other)
        return self

    setattr(self, "__rshift__", __rshift__)

    def __rrshift__(other, self, *args, **kwargs):
        """Called for [task1, task2] >> task3 because list don't have __rshift__ operators.
        Therefore we reverse the order of the arguments and call __rshift__"""
        __rshift__(self=self, other=other)

    setattr(self, "__rrshift__", __rrshift__)
    return self


def _set_workflow(workflow):
    __workflow.set(workflow)


def _get_workflow():
    try:
        return __workflow.get()
    except LookupError:
        return None


def _handle_first(self):
    work_flow = _get_workflow()
    if not work_flow.chain_of_tasks:
        _connect(self)


def _connect(job):
    if isinstance(job, list):
        _connect_parallel_job(job)
    else:
        _connect_single_job(job)


def _connect_parallel_job(job):
    work_flow = _get_workflow()
    work_flow.add_parallel_tasks(job)
    return job


def _connect_single_job(job):
    work_flow = _get_workflow()
    work_flow.add_task(job)
    return job
