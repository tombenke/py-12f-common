"""
The central logger module of the application

This module defines a module-level singleton of logger,
that the other parts of the application can use within the trivial name of ``logger``.

It is also responsible to make the logger configable, via the selected parameters,
in the meaning of setting the ``LOG_LEVEL`` and the ``LOG_FORMAT``.

The module provides helper functions to access to the logger instance,
as well as to enable the command line parser to gain the list of possible choices for log level and format.
"""
import sys
from loguru import logger

# Use the loguru as logger
app_logger = logger


def get_level_choices():
    """
    Provides the list of valid log level names

    :return Array[str]: The array of log-level names possible to use within the actual implementation of the logger.
    """
    return ["critical", "error", "warning", "success", "info", "debug", "trace"]


def get_format_choices():
    """
    Provides the list of valid log format names

    :return Array[str]: The array of log-formats possible to use within the actual implementation of the logger.
    """

    return ["text", "json"]


def get_logger():
    """
    Returns with the application logger

    :return: the logger object
    """
    return app_logger


def init_logger(log_level: str, log_format: str):
    """
    Configures the logger instance

    :param str log_level: The selected log level to use.
    :param str log_format: The selected log format to use.

    :return: the logger object
    """
    # Remove the default logger before configuring
    app_logger.remove()

    if log_level is None:
        log_level = "info"

    if log_format is None:
        log_format = "text"

    # Create a new sink instance, and set the format and level
    if log_format.upper() == "JSON":
        app_logger.add(sys.stderr, level=log_level.upper(), serialize=True)
    else:
        app_logger.add(sys.stderr, level=log_level.upper())

    return app_logger
