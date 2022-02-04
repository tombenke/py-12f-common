"""
This module holds a base class for generic, asynchronous applications with config, logging and graceful shut-down.

It contains the ``ApplicationBase`` base class for application
accompanied with the ``terminate()`` helper function that shuts the application down on a graceful way.

The module also provides the ``application_entrypoint`` which implements a generic entrypoint to an application.
It helps to significantly shorten the boilerplate, which every application needs to have.
"""
from .app_base import ApplicationBase
from .app_entrypoint import application_entrypoint
from .app_terminate import terminate

__all__ = ["app_base", "app_entrypoint"]
