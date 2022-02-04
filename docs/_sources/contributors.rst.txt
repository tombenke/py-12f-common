Contributors
============

Install
-------

If you want to install the code for the purpose of developing the library,
then fork and clone `the GitHub repository
<https://github.com/tombenke/py-12f-common>`_.



Prerequisites
~~~~~~~~~~~~~
- Python3
- `Task <https://taskfile.dev/#/>`_

Install Python and module dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install Python 3, using some virtual environment.

Create and switch to a virtual environment dedicated to this project.

For development, install the package and its dependencies in editable mode, using task:

.. code-block:: console

    task install-dev-editable


or directly with the pip command:

.. code-block:: console

    pip install -e .[dev] .


.. note::

    The ``task install-...`` tasks also installs git hooks (e.g. pre-commit).
    The git hooks are simple bash scripts, that call tasks, for example the `pre-commit` hook will call the `task pre-commit` command.

Usage of tasks
--------------

List the available tasks:

.. code-block:: console

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


Run tests:

.. code-block:: console

    task test-verbose

