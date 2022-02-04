"""Terminator module"""
# import signal
from common.logger import get_logger


class TerminalException(BaseException):
    """
    Customer exception.

    Raise this to terminate the running of applications.
    """


def terminate():
    """
    Terminator function.

    Its call will kill the application.
    """
    get_logger().info("Terminate the application")
    raise TerminalException
