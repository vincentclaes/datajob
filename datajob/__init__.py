import logging
import os
import pathlib
import shlex
import subprocess
from pathlib import Path

from rich.console import Console

ROOT_DIR = pathlib.Path(__file__).parent.absolute()
DEFAULT_STACK_STAGE = "dev"
# if someone tried to log something before basicConfig is called, Python creates a default handler that
# goes to the console and will ignore further basicConfig calls. Remove the handler if there is one.
# https://stackoverflow.com/a/45624044/1771155
root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
log_level = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=logging.getLevelName(log_level))
project_name = Path(__file__).parent.stem
logger = logging.getLogger(project_name)


def call_subprocess(cmd: str) -> None:
    """
    call a command as a subprocess in a secure way.
    https://stackoverflow.com/a/59090212/1771155
    :param cmd: the command to execute
    :return: None
    """
    print(f"datajob subprocess command: " f"{cmd}")
    subprocess.check_call(shlex.split(cmd))


console = Console(style="bold green", soft_wrap=True, log_path=False)
