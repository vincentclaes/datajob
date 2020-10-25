import pathlib

from aws_cdk import core

from tech_skills_parser import logger
from tech_skills_parser.deployment.tech_skills_parser_stack import TechSkillsParserStack
from tech_skills_parser.deployment.stepfunctions_workflow import StepfunctionsWorkflow

project_root = str(pathlib.Path(__file__).parent.absolute())

app = core.App()

stage_context = app.node.try_get_context("stage")
if not stage_context:
    raise ValueError(
        "we expect a stage to be set on the cli. e.g 'cdk deploy -c stage=my-stage'"
    )
stage = stage_context

unique_stack_name = f"tech-skills-parser-{stage}"

logger.info(f"deploying application {unique_stack_name}")
logger.info(f"stage for this deployment {stage}")

stack = TechSkillsParserStack(
    scope=app,
    unique_stack_name=unique_stack_name,
    stage=stage,
    project_root=project_root,
    env={"region": "eu-west-1", "account": "303915887687"},
    include_folder="tech_skills_parser/",
)

app.synth()

# todo - generate role dynamically
with StepfunctionsWorkflow(
    "techskills-parser",
    "arn:aws:iam::303915887687:role/tech-skills-parser-orchestration",
) as tech_skills_parser_orchestration:

    [
        stack.glue_job_keywords_cleaning,
        stack.glue_job_vacancy_cleaning,
    ] >> stack.glue_job_create_tf_matrix

print("**************************************")
print(
    f"url for step functions workflow: https://{stack.region}.console.aws.amazon.com/states/home?region={stack.region}#/statemachines/view/{tech_skills_parser_orchestration.workflow.state_machine_arn}"
)
print("**************************************")
