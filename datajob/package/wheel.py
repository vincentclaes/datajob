import subprocess
from pathlib import Path

from datajob import logger


class DatajobPackageWheelError(Exception):
    """any exception occuring when constructing a wheel in data job context."""


def create(project_root):
    """launch a subprocess to built a wheel.
    todo - use the setuptools/disttools api to create a setup.py.
    relying on a subprocess feels dangerous.
    """
    setup_py_file = Path(project_root, "setup.py")
    if setup_py_file.is_file():
        logger.debug(f"found a setup.py file in {project_root}")
        logger.debug("creating wheel for glue job")
        cmd = f"cd {project_root}; python setup.py bdist_wheel"
        print(f"wheel command: {cmd}")
        # todo - shell=True is not secure
        subprocess.call(cmd, shell=True)
    else:
        raise DatajobPackageWheelError(
            f"no setup.py file detected in project root {project_root}. "
            f"Hence we cannot create a python wheel for this project"
        )
