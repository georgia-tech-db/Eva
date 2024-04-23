###############################
### EvaDB PACKAGAGING
###############################

import io
import os

# to read contents of README file
from pathlib import Path
from typing import Dict

from setuptools import find_packages, setup
from setuptools.command.install import install
from subprocess import check_call

this_directory = Path(__file__).parent
LONG_DESCRIPTION = (this_directory / "README.md").read_text()

DESCRIPTION = "EvaDB AI-Relational Database System"
NAME = "evadb"
AUTHOR = "Georgia Tech Database Group"
AUTHOR_EMAIL = "arulraj@gatech.edu"
URL = "https://github.com/georgia-tech-db/eva"

# Check Python version
# import sys
# if sys.version_info < (3, 8):
#     sys.exit("Python 3.8 or later is required.")


def read(path, encoding="utf-8"):
    path = os.path.join(os.path.dirname(__file__), path)
    with io.open(path, encoding=encoding) as fp:
        return fp.read()


# version.py defines the VERSION and VERSION_SHORT variables
VERSION_DICT: Dict[str, str] = {}
with open("evadb/version.py", "r") as version_file:
    exec(version_file.read(), VERSION_DICT)

DOWNLOAD_URL = "https://github.com/georgia-tech-db/eva"
LICENSE = "Apache License 2.0"
VERSION = VERSION_DICT["VERSION"]

minimal_requirements = [
    "numpy>=1.19.5",
    "pandas>=2.1.0", # DataFrame.map is available after v2.1.0
    "sqlalchemy>=2.0.0",
    "sqlalchemy-utils>=0.36.6",
    "lark>=1.0.0",
    "pyyaml>=5.1",
    "aenum>=2.2.0",
    "diskcache>=5.4.0",
    "retry>=0.9.2",
    "pydantic<2",  # ray-project/ray#37019.
    "psutil",
    "thefuzz",
]

vision_libs = [
    "torch>=1.10.0",
    "torchvision>=0.11.1",
    "transformers",  # HUGGINGFACE
    "faiss-cpu",  # DEFAULT VECTOR INDEX
    "opencv-python-headless>=4.6.0.66",
    "Pillow>=8.4.0",
    "eva-decord>=0.6.1",  # VIDEO PROCESSING
    "ultralytics>=8.0.93",  # OBJECT DETECTION
    "timm>=0.6.13",  # HUGGINGFACE VISION TASKS
    "sentencepiece",  # TRANSFORMERS
]

document_libs = [
    "transformers",  # HUGGINGFACE
    "langchain",  # DATA LOADERS
    "faiss-cpu",  # DEFAULT VECTOR INDEX
    "pymupdf<1.23.0",  # pymupdf/PyMuPDF#2617 and pymupdf/PyMuPDF#2614
    "pdfminer.six",
    "sentence-transformers",
    "protobuf",
    "bs4",
    "openai>=1.0",  # CHATGPT
    "gpt4all",  # PRIVATE GPT
    "sentencepiece",  # TRANSFORMERS
]

function_libs = [
    "facenet-pytorch>=2.5.2",  # FACE DETECTION
    "pytube",  # YOUTUBE QA APP
    "youtube-transcript-api",  # YOUTUBE QA APP
    "boto3",  # AWS
    "norfair>=2.2.0",  # OBJECT TRACKING
    "kornia",  # SIFT FEATURES
]

ray_libs = [
    "ray>=1.13.0,<2.5.0",  # BREAKING CHANGES IN 2.5.0
]

notebook_libs = [
    "ipython<8.13.0",
    "ipywidgets>=7.7.2",
    "matplotlib>=3.3.4",
    "nbmake>=1.2.1",
    "nest-asyncio>=1.5.6",
]

qdrant_libs = ["qdrant_client"]  # cannot install on 3.11 due to grcpio

pinecone_libs = ["pinecone-client"]

chromadb_libs = ["chromadb"]

weaviate_libs = ["weaviate-client"]

milvus_libs = ["pymilvus>=2.3.0"]


postgres_libs = [
    "psycopg2",
]

ludwig_libs = ["ludwig[hyperopt,distributed]"]  # MODEL TRAIN AND FINE TUNING

sklearn_libs = ["scikit-learn"]

xgboost_libs = ["flaml[automl]"]

hackernews_libs = ["requests"]

forecasting_libs = [
    "statsforecast",  # MODEL TRAIN AND FINE TUNING
    "neuralforecast",  # MODEL TRAIN AND FINE TUNING
]

imagegen_libs = [
    "replicate"
]

reddit_libs = [
    "praw"
]

### NEEDED FOR DEVELOPER TESTING ONLY

dev_libs = [
    # TESTING PACKAGES
    "pytest>=6.1.2",
    "pytest-cov>=2.11.1",
    "mock",
    "coveralls>=3.0.1",
    "moto[s3]>=4.1.1",
    "pytest-testmon",
    # BENCHMARK PACKAGES
    "pytest-benchmark",
    # LINTING PACKAGES
    "codespell",
    "pylint",
    "black>=23.1.0",
    "isort>=5.10.1",
    "flake8>=3.9.1",
    # DISTRIBUTION PACKAGES
    "wheel>=0.37.1",
    "semantic_version",
    "PyGithub",
    "twine",
    "PyDriller",
]

INSTALL_REQUIRES = minimal_requirements

EXTRA_REQUIRES = {
    "ray": ray_libs,
    "vision": vision_libs,
    "document": document_libs,
    "function": function_libs,
    "notebook": notebook_libs,
    "qdrant": qdrant_libs,
    "pinecone": pinecone_libs,
    "chromadb": chromadb_libs,
    "milvus": milvus_libs,
    "weaviate": weaviate_libs,
    "postgres": postgres_libs,
    "ludwig": ludwig_libs,
    "sklearn": sklearn_libs,
    "xgboost": xgboost_libs,
    "forecasting": forecasting_libs,
    "hackernews": hackernews_libs,
    "reddit": reddit_libs,
    # everything except ray, qdrant, ludwig and postgres. The first three fail on pyhton 3.11.
    "dev": dev_libs + vision_libs + document_libs + function_libs + notebook_libs + forecasting_libs + sklearn_libs + imagegen_libs + xgboost_libs + reddit_libs
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
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        # "Programming Language :: Python :: 3.11",
    ],
    packages=find_packages(exclude=["tests", "tests.*"]),
    # https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html#the-console-scripts-entry-point
    entry_points={
        "console_scripts": [
            "evadb_server=evadb.evadb_server:main",
            "evadb_client=evadb.evadb_cmd_client:main",
        ]
    },
    python_requires=">=3.8",
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRA_REQUIRES,
    include_package_data=True,
    package_data={
        "evadb": [
            "evadb.yml",
            "parser/evadb.lark",
            "third_party/databases/**/requirements.txt",
        ]
    },
)
