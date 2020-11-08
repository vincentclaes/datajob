import pathlib
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()

setup(
    name="glue_job_include_packaged_project",  # Required
    version="latest",  # Required
    description="A sample Python project",  # Optional
    author="A. Random Developer",  # Optional
    author_email="author@example.com",  # Optional
    package_dir={"": "glue_job_include_packaged_project"},  # Optional
    packages=find_packages(where="glue_job_include_packaged_project"),  # Required
)
