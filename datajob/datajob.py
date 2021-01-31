import os
import pathlib
import shlex
import subprocess
from pathlib import Path

import typer

from datajob.package import wheel

app = typer.Typer()
filepath = pathlib.Path(__file__).resolve().parent


def run():
    """entrypoint for datajob"""
    app()


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def deploy(
    stage: str = typer.Option(None),
    config: str = typer.Option(Path, callback=os.path.abspath),
    package: str = typer.Option(None, "--package"),
    ctx: typer.Context = typer.Option(list),
):
    if package:
        # todo - check if we are building in the right directory
        project_root = str(Path(config).parent)
        wheel.create_wheel(project_root=project_root, package=package)
    # create stepfunctions if requested
    # make sure you have quotes around the app arguments
    args = ["--app", f""" "python {config}" """, "-c", f"stage={stage}"]
    extra_args = ctx.args
    call_cdk(command="deploy", args=args, extra_args=extra_args)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def synthesize(
    stage: str = typer.Option(None),
    config: str = typer.Option(Path, callback=os.path.abspath),
    ctx: typer.Context = typer.Option(list),
):
    args = ["--app", f""" "python {config}" """, "-c", f"stage={stage}"]
    extra_args = ctx.args
    call_cdk(command="synthesize", args=args, extra_args=extra_args)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def destroy(
    stage: str = typer.Option(None),
    config: str = typer.Option(Path, callback=os.path.abspath),
    ctx: typer.Context = typer.Option(list),
):
    args = ["--app", f""" "python {config}" """, "-c", f"stage={stage}"]
    extra_args = ctx.args
    call_cdk(command="destroy", args=args, extra_args=extra_args)


def call_cdk(command: str, args: list = None, extra_args: list = None):
    args = args if args else []
    extra_args = extra_args if extra_args else []
    full_command = " ".join(["cdk", command] + args + extra_args)
    print(f"cdk command:" f" {full_command}")
    # todo - shell=True is not secure
    # subprocess.call(full_command, shell=True)
    subprocess.check_call(shlex.split(full_command))
