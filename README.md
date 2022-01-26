# py-12f-common

[![Quality Check Status](https://github.com/tombenke/py-12f-common/workflows/Quality%20Check/badge.svg)](https://github.com/tombenke/py-12f-common)
![Coverage](./coverage.svg)

## About

This repository holds those infrastructure-level modules,
that every application requires that follows the core 12-factor principles.

## Install

### Prerequisites
- Python3
- [Task](https://taskfile.dev/#/)

### Install Python and module dependencies

Install Python 3, using some virtual environment.

Create and switch to a virtual environment dedicated to this project.

For development, install the package and its dependencies in editable mode, using task:

```bash
    task install-dev-editable
```

or directly with the pip command:

```bash
    pip install -e .[dev] .
```

NOTE:
The `task install-...` tasks also installs git hooks (e.g. pre-commit).
The git hooks are simple bash scripts, that call tasks, for example the `pre-commit` hook will call the `task pre-commit` command.

## Usage

List the available tasks:

```bash
    task list

    task: Available tasks for this project:
    * build-docker:         Build docker image
    * clean:                Clean temporary files and folders
    * coverage:             Test coverage
    * default:              Executes all the tests then build the binary.
    * docs:                 Generate module documentation into the docs/ folder
    * format:               Autoformat the source files
    * install:              Install the package and its dependencies
    * install-dev:          Install the package and its dependencies for development
    * install-dev-editable: Install the package and its dependencies for development with editablility
    * install-git-hooks:    Install git hooks
    * lint:                 Run python linter
    * pre-commit:           Runs the QA tasks from a git pre-commit hook
    * test:                 Run all the tests.
    * test-verbose:         Run all the go tests.
```

Run tests:

```bash
    task test-verbose
```

## References

## Development tools
- [Black - code formatter](https://pypi.org/project/black/)
- [Coverage.py](https://github.com/nedbat/coveragepy)
- [Pylint](https://github.com/PyCQA/pylint)
- [Task](https://taskfile.dev/#/)
