import pathlib
from setuptools import setup, find_packages

here = str(pathlib.Path(__file__).parent.resolve())

setup(
    name="simple_data_pipeline",  # Required
    version="latest",  # Required
    description="A sample Python project",  # Optional
    author="A. Random Developer",  # Optional
    author_email="author@example.com",  # Optional
    install_requires=[],
    packages=find_packages(where=here),  # Required
)
