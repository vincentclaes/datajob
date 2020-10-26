import pathlib

from aws_cdk import core

from datajob.tech_skills_parser_stack import TechSkillsParserStack
from datajob import logger

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

