import typer
import subprocess
from datajob.package import wheel
import pathlib
from pathlib import Path

app = typer.Typer()
filepath = pathlib.Path(__file__).resolve().parent


def run():
    """entrypoint for datajob"""
    app()


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def deploy(
    config: str = typer.Option(...),
    package: bool = typer.Option(False, "--package"),
    ctx: typer.Context = typer.Option(list),
):
    if package:
        wheel.create(project_root=package)
    # create stepfunctions if requested
    args = ["--app", f"python {config}"]
    extra_args = ctx.args
    call_cdk(command="deploy", args=args, extra_args=extra_args)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def orchestrate(config: str = typer.Option(...)):
    pass


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def destroy(config: str = typer.Option(...)):
    call_cdk(command="destroy", args=" ".join(["--app", f"python {config}"]))


def call_cdk(command: str, args: list = None, extra_args: list = None):
    args = args if args else []
    extra_args = extra_args if extra_args else []
    subprocess.call(" ".join(["cdk", command] + args + extra_args), shell=True)
