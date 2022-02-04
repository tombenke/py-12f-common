"""
The common packages is made of the following sub-modules:
    - *app*: A base class for generic, asynchronous applications with config, logging and graceful shut-down.
    - *config*: A configuration class, to collect and access to deployment-dependend configuration parameters.
    - *logger*: A simple, central logger used by the application.
"""

__all__ = ["app", "config", "logger"]
