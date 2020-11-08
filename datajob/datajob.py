import typer
import subprocess

app = typer.Typer()


def run():
    """entrypoint for datajob"""
    app()


@app.command()
def deploy(config: str):
    call_cdk(command="deploy", args=" ".join(["--app", f"python {config}"]))


@app.command()
def orchestrate(file_name: str):
    pass


@app.command()
def destroy(file_name: str):
    pass


def call_cdk(command, args):
    subprocess.call(" ".join(["cdk", command, args]), shell=True)