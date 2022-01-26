"""The central logger module of the application"""
import sys
from loguru import logger

# Use the loguru as logger
app_logger = logger


def get_level_choices():
    """Provides the list of valid log level names"""
    return ["critical", "error", "warning", "success", "info", "debug", "trace"]


def get_format_choices():
    """Provides the list of valid log format names"""
    return ["text", "json"]


def get_logger():
    """Returns with the application logger"""
    return app_logger


def init_logger(log_level: str, log_format: str):
    """Configures the logger instance"""
    # Remove the default logger before configuring
    app_logger.remove()

    # Create a new sink instance, and set the format and level
    if log_format.upper() == "JSON":
        app_logger.add(sys.stderr, level=log_level.upper(), serialize=True)
    else:
        app_logger.add(sys.stderr, level=log_level.upper())

    return app_logger
