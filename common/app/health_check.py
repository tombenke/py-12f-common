"""
Health check
"""
from enum import Enum
from typing import List

from flask import Flask


class State(Enum):
    """
    Possible microservice states
    """

    STOP = "Stopped"
    WARMUP = "Warming up"
    WORK = "Working"
    SHUTDOWN = "Shutting down"
    NOINFO = "No information"


class Status(Enum):
    """
    Possible statuses the api can return
    """

    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"


# pylint: disable=too-few-public-methods
class Response:
    """
    Parent class of different responses
    """

    status: Status
    notes: List[str]

    def __init__(self, service_name: str):
        self.service_name = service_name

    @property
    def create_response(self):
        """
        Composes the response to an http request
        """
        return {
            "status": self.status.value,
            "notes": self.notes,
            "description": f"Health state of '{self.service_name}' microservice",
        }


# pylint: disable=too-few-public-methods
class Pass(Response):
    """
    Response of passed status.
    For "pass" status, HTTP response code in the 2xx-3xx range MUST be used.
    """

    status = Status.PASS
    status_code = 200
    notes = ["Service is running"]


# pylint: disable=too-few-public-methods
class Fail(Response):
    """
    Response of failed status.
    For "fail" status, HTTP response code in the 4xx-5xx range MUST be used.
    """

    status = Status.FAIL
    status_code = 503
    notes = ["Service is not running"]


# pylint: disable=too-few-public-methods
class Warn(Response):
    """
    Response of warning status.
    In case of the "warn" status, endpoints MUST return HTTP status in the 2xx-3xx range, and additional information
    SHOULD be provided, utilizing optional fields of the response.
    """

    status = Status.WARN
    status_code = 203
    notes = ["Service is not healthy"]


class HealthCheck:
    """
    Class for running api server to access the health endpoint
    """

    def __init__(self, service_name: str, port=5000):
        self.service_name = service_name
        self.port = port
        self.service_state = State.NOINFO

        self.app = Flask(__name__)
        self.app.add_url_rule("/health", "health", self.health)

    def start_server(self):
        """
        Start the api server
        """
        self.app.run(port=self.port)

    def set_service_state(self, state: State):
        """
        Sets the service state
        """
        self.service_state = state

    def health(self):
        """
        Health check endpoint
        """
        if self.service_state == State.WORK:
            resp = Pass(self.service_name)
        elif self.service_state == State.STOP:
            resp = Fail(self.service_name)
        else:
            resp = Warn(self.service_name)

        return resp.create_response, resp.status_code


if __name__ == "__main__":
    hc = HealthCheck("sth", 5000)
    hc.start_server()
