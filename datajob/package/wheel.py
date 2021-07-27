from pathlib import Path

from datajob import call_subprocess
from datajob import logger


class DatajobPackageWheelError(Exception):
    """any exception occuring when constructing a wheel in data job context."""


def create_wheel(project_root: str, package: str) -> None:
    """Select the function to build a wheel based on the argument provided
    with.

    --package. At the time of writing the argument can be setuppy or poetry.

    :param project_root: the path to the root of your project.
    :param package: the tool you want to use to build your wheel using (setuppy, poetry, ...)
    :return: None
    """
    wheel_functions = {"setuppy": _setuppy_wheel, "poetry": _poetry_wheel}
    wheel_functions[package](project_root)


def _setuppy_wheel(project_root: str) -> None:
    """build a wheel for your project using poetry.

    :param project_root: the path to the root of your project.
    :return: None
    """
    _execute_packaging_logic(
        project_root=project_root,
        config_file="setup.py",
        cmd="python setup.py bdist_wheel",
    )


def _poetry_wheel(project_root: str) -> None:
    """build a wheel for your project using poetry.

    :param project_root: the path to the root of your project.
    :return: None
    """
    _execute_packaging_logic(
        project_root=project_root, config_file="pyproject.toml", cmd="poetry build"
    )


def _execute_packaging_logic(project_root: str, config_file: str, cmd: str) -> None:
    """check if the config file exists in the project root and execute the
    command to create a wheel.

    :param project_root: the path to the root of your project.
    :param config_file: the confgi file to package the project as a wheel (setup.py or pyproject.toml)
    :param cmd: the command to execute to create a wheel.
    :return: None
    """
    config_file_full_path = Path(project_root, config_file)
    logger.info(f"expecting {config_file_full_path}")
    if not config_file_full_path.is_file():
        raise DatajobPackageWheelError(
            f"no {config_file} file detected in project root {project_root}. "
            f"Hence we cannot create a python wheel for this project"
        )

    logger.debug(f"found a {config_file} file in {project_root}")
    call_subprocess(cmd=cmd)
