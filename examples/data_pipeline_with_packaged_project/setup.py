import pathlib
from setuptools import setup, find_packages

here = str(pathlib.Path(__file__).parent.resolve())

setup(
    name="data_pipeline_with_packaged_project",  # Required
    version="latest",  # Required
    description="A sample Python project",  # Optional
    author="A. Random Developer",  # Optional
    author_email="author@example.com",  # Optional
    install_requires=[],
    packages=find_packages(where=here),  # Required
)
