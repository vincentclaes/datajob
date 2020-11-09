import subprocess
from pathlib import Path

from aws_cdk import aws_iam as iam, core, aws_s3_deployment, aws_s3
from aws_empty_bucket.empty_s3_bucket import EmptyS3Bucket

from datajob import logger


class DatajobPackageWheelError(Exception):
    """any exception occuring when constructing wheel in data job context."""


def create(project_root):
    """launch a subprocess to built a wheel.

    todo - use the setuptools/disttools api to create a setup.py.
    relying on a subprocess feels dangerous.
    """
    setup_py_file = Path(project_root, "setup.py")
    if setup_py_file.is_file():
        logger.debug(f"found a setup.py file in {project_root}")
        logger.debug("creating wheel for glue_job_include_packaged_project job")
        cmd = f"cd {project_root}; python setup.py bdist_wheel"
        subprocess.call(cmd, shell=True)
    else:
        raise DatajobPackageWheelError(
            f"no setup.py file detected in project root {project_root}. "
            f"Hence we cannot create a python wheel for this project"
        )
