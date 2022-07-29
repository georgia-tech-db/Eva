###############################
### EVA PACKAGAGING
###############################

import io
import os
import re

# to read contents of README file
from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
LONG_DESCRIPTION = (this_directory / "README.md").read_text()

DESCRIPTION = "EVA Video Database System (Think MySQL for videos)."
NAME = "evadb"
AUTHOR = "Georgia Tech Database Group"
AUTHOR_EMAIL = "georgia.tech.db@gmail.com"
URL = "https://github.com/georgia-tech-db/eva"


def read(path, encoding="utf-8"):
    path = os.path.join(os.path.dirname(__file__), path)
    with io.open(path, encoding=encoding) as fp:
        return fp.read()


def version(path):
    """Obtain the package version from a python file e.g. pkg/__init__.py
    See <https://packaging.python.org/en/latest/single_source_version.html>.
    """
    version_file = read(path)
    version_match = re.search(
        r"""^__version__ = ['"]([^'"]*)['"]""", version_file, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


DOWNLOAD_URL = "https://github.com/georgia-tech-db/eva"
LICENSE = "Apache License 2.0"
VERSION = version("eva/version.py")

minimal_requirement = [
    "numpy==1.20.1",
    "opencv-python==4.5.1.48",
    "pandas==1.2.3",
    "torch==1.7.1",
    "torchvision==0.8.2",
    "Pillow==8.1.2",
    "sqlalchemy==1.3.20",
    "sqlalchemy-utils==0.36.6",
    "pyspark==3.0.2",
    "petastorm==0.9.8",
    "antlr4-python3-runtime==4.8",
    "pyyaml==5.1",
    "pymysql==0.10.1",
]

formatter_libs = ["black", "isort"]

extra_test_libs = [
    "flake8",
]

integration_test_libs = []

core_test_libs = [
    "pytest",
    # Coveralls doesn't work with 6.0
    # https://github.com/TheKevJames/coveralls-python/issues/326
    "coverage[toml]<6.0",
    "pytest-cov",
    "pytest-virtualenv",
    "coveralls",
]
benchmark_libs = [
]

doc_libs = [
]

database_libs = [
]

MINIMAL_REQUIRES = minimal_requirement
INSTALL_REQUIRES = minimal_requirement + formatter_libs
DATABASE_REQUIRES = INSTALL_REQUIRES + database_libs
DEV_REQUIRES = (
    minimal_requirement
    + formatter_libs
    + database_libs
    + integration_test_libs
    + extra_test_libs
    + core_test_libs
    + benchmark_libs
    + doc_libs
)

EXTRA_REQUIRES = {
    "dev": DEV_REQUIRES,
    "database": DATABASE_REQUIRES,
    "minimal": MINIMAL_REQUIRES,
}

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
    license=LICENSE,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License"
        "Operating System :: OS Independent"
    ],
    packages=find_packages(exclude=[
        "tests", 
        "tests.*"
    ]),
    # https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html#the-console-scripts-entry-point
    entry_points={"console_scripts": [
        "eva_server=eva.eva_server:main",
        "eva_client=eva.eva_cmd_client:main"
    ]},
    python_requires=">=3.8",
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRA_REQUIRES,
    include_package_data=True,
    package_data={"eva": ["eva.yml"]}
)
