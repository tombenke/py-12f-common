from setuptools import find_packages, setup
import pathlib
import os

# Package metadata
# ----------------
APP_NAME = "py-12f-common"
APP_DESCRIPTION = """This repository holds those infrastructure-level modules, that every application requires that follows the core 12-factor principles."""

# Get the long description from the README file
HERE = pathlib.Path(__file__).parent.resolve()
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding="utf-8")

URL = "https://github.com/tombenke/py-12f-common"
EMAIL = "tombenke@gmail.com"
AUTHOR = "Tamás Benke"
LICENSE = "MIT"
REQUIRES_PYTHON = ">=3.8"

# What packages are required for this module to be executed?
REQUIRED = [
    "argparse",
    "dataclasses",
    "loguru",
]

DEV_REQUIREMENTS = [
    "build",
    "coverage",
    "coverage-badge",
    "black",
    "pdoc",
    "pydeps",
    "pylint",
]

setup(
    name=APP_NAME,
    version=os.getenv("VERSION", "1.0.0"),
    description=APP_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    license=LICENSE,
    packages=find_packages(exclude=("tests", "docs")),
    include_package_data=True,
    install_requires=REQUIRED,
    extras_require={"dev": DEV_REQUIREMENTS},
    entry_points={},
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
)
