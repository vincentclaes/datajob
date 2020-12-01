import pathlib
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()

setup(
    name="simple_data_pipeline",  # Required
    version="latest",  # Required
    description="A sample Python project",  # Optional
    author="A. Random Developer",  # Optional
    author_email="author@example.com",  # Optional
    package_dir={"": "simple_data_pipeline"},  # Optional
    packages=find_packages(where="simple_data_pipeline"),  # Required
)
