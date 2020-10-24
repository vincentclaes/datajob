import logging
import os
import pathlib
from pathlib import Path

ROOT_DIR = pathlib.Path(__file__).parent.absolute()

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
