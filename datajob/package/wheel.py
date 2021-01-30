import subprocess
from pathlib import Path

from datajob import logger


class DatajobPackageWheelError(Exception):
    """any exception occuring when constructing a wheel in data job context."""


def create_wheel(project_root: str, package: str) -> None:
    """
    Select the function to build a wheel based on the argument provided with --package.
    At the time of writing this can be (setuppy or poetry)
    :param project_root: the path to the root of your project.
    :param package: the tool you want to use to build your wheel using (setuppy, poetry, ...)
    :return: None
    """
    wheel_functions = {"setuppy": _setuppy_wheel, "poetry": _poetry_wheel}
    wheel_functions[package](project_root)


def _setuppy_wheel(project_root: str) -> None:
    """
    build a wheel for your project using poetry.
    :param project_root: the path to the root of your project.
    :return: None
    """
    setup_py_file = Path(project_root, "setup.py")
    if setup_py_file.is_file():
        logger.debug(f"found a setup.py file in {project_root}")
        cmd = f"cd {project_root}; python setup.py bdist_wheel"
        _call_create_wheel_command(cmd=cmd)
    else:
        raise DatajobPackageWheelError(
            f"no setup.py file detected in project root {project_root}. "
            f"Hence we cannot create a python wheel for this project"
        )


def _poetry_wheel(project_root):
    """
    build a wheel for your project using poetry.
    :param project_root: the path to the root of your project.
    :return: None
    """
    poetry_file = Path(project_root, "pyproject.toml")
    if poetry_file.is_file():
        logger.debug(f"found a pyproject.toml file in {project_root}")
        cmd = f"cd {project_root}; poetry build"
        _call_create_wheel_command(cmd=cmd)
    else:
        raise DatajobPackageWheelError(
            f"no pyproject.toml file detected in project root {project_root}. "
            f"Hence we cannot create a python wheel for this project"
        )


def _call_create_wheel_command(cmd: str) -> None:
    """shell out and call the command to create the wheel."""
    logger.debug("creating wheel")
    print(f"wheel command: {cmd}")
    # todo - shell=True is not secure
    subprocess.call(cmd, shell=True)
