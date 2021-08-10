import os
import pathlib
import shlex
import subprocess
from pathlib import Path

import typer
from stepfunctions.workflow.widgets.utils import create_sfn_execution_url

from datajob import console
from datajob.package import wheel
from datajob.stepfunctions import stepfunctions_execute

app = typer.Typer()
filepath = pathlib.Path(__file__).resolve().parent


def run():
    """entrypoint for datajob."""
    app()


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def deploy(
    stage: str = typer.Option(
        None,
        help="the stage of the data pipeline stack you would like to deploy (dev/stg/prd/ ...)",
    ),
    config: str = typer.Option(
        Path,
        callback=os.path.abspath,
        help="the path to the python file that describes our data pipeline.",
    ),
    package: str = typer.Option(
        None, "--package", help="specify 'poetry' or 'setuppy' to package the project."
    ),
    ctx: typer.Context = typer.Option(
        list, help="any extra cdk cli args you might want to pass."
    ),
):
    if package:
        project_root = str(Path(config).parent)
        wheel.create_wheel(project_root=project_root, package=package)
    # create stepfunctions if requested
    # make sure you have quotes around the app argument
    args = ["--app", f""" "python {config}" """, "-c", f"stage={stage}"]
    extra_args = ctx.args
    call_cdk(command="deploy", args=args, extra_args=extra_args)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def synthesize(
    stage: str = typer.Option(
        None,
        help="the stage of the data pipeline stack you would like to synthesize (dev/stg/prd/ ...)",
    ),
    config: str = typer.Option(
        Path,
        callback=os.path.abspath,
        help="the path to the python file that describes our data pipeline.",
    ),
    ctx: typer.Context = typer.Option(
        list, help="any extra cdk cli args you might want to pass."
    ),
):
    args = ["--app", f""" "python {config}" """, "-c", f"stage={stage}"]
    extra_args = ctx.args
    call_cdk(command="synthesize", args=args, extra_args=extra_args)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def destroy(
    stage: str = typer.Option(
        None,
        help="the stage of the data pipeline stack you would like to destroy (dev/stg/prd/ ...)",
    ),
    config: str = typer.Option(
        Path,
        callback=os.path.abspath,
        help="the path to the python file that describes our data pipeline.",
    ),
    ctx: typer.Context = typer.Option(
        list, help="any extra cdk cli args you might want to pass."
    ),
):
    args = ["--app", f""" "python {config}" """, "-c", f"stage={stage}"]
    extra_args = ctx.args
    call_cdk(command="destroy", args=args, extra_args=extra_args)


def call_cdk(command: str, args: list = None, extra_args: list = None):
    args = args or []
    extra_args = extra_args or []
    full_command = " ".join(["cdk", command] + args + extra_args)
    print(f"cdk command:" f" {full_command}")
    subprocess.check_call(shlex.split(full_command))


@app.command()
def execute(
    state_machine: str = typer.Option(
        ..., help="the full name of the state machine you want to execute."
    )
):
    state_machine_arn = stepfunctions_execute.find_state_machine_arn(state_machine)
    execution_input = stepfunctions_execute.get_execution_input(
        sfn_arn=state_machine_arn
    )
    console.log(f"executing: {state_machine}")
    execution = stepfunctions_execute.execute(
        state_machine_arn, execution_input=execution_input
    )
    status = stepfunctions_execute.get_status(execution)
    console.log(f"status: {status}")
    url = create_sfn_execution_url(execution.execution_arn)
    console.log(f"view the execution on the AWS console:")
    console.log(f"")
    console.print(f"{url}", soft_wrap=True)
    console.log(f"")
