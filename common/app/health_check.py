"""
Health check module. It runs a web service on localhost and the specified port. The health state of the application can
be queried at the 'health' end point.


The implementation of health check response is based on 'Health Check Response Format for HTTP APIs'
(https://datatracker.ietf.org/doc/html/draft-inadarei-api-health-check-06)
"""
from enum import Enum
from typing import List

from aiohttp import web


class State(Enum):
    """
    Possible microservice states
    """

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
            "serviceId": "get-health",
            "description": f"Returns the health of the '{self.service_name}' service",
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
    notes = ["No information about the service"]


# pylint: disable=too-few-public-methods
class Warn(Response):
    """
    Response of warning status.
    In case of the "warn" status, endpoints MUST return HTTP status in the 2xx-3xx range, and additional information
    SHOULD be provided, utilizing optional fields of the response.
    """

    status = Status.WARN
    status_code = 202
    notes = ["Service is not healthy, it is warming up or shutting down"]


class HealthCheck:
    """
    Class for running web service to access the 'health' endpoint
    """

    def __init__(self, logger, service_name: str, port=8008):
        self.logger = logger
        self.service_name = service_name
        self.port = port
        self.service_state = State.NOINFO

        self.app = web.Application()
        self.app.router.add_get("/health", self.health)

    async def health(self, _msg):
        """
        Handler for the health check endpoint. The response is in JSON format.
        """
        if self.service_state == State.WORK:
            resp = Pass(self.service_name)
        elif self.service_state == State.NOINFO:
            resp = Fail(self.service_name)
        else:
            resp = Warn(self.service_name)

        return web.json_response(resp.create_response, status=resp.status_code)

    async def run_server(self):
        """
        Run the web service on localhost and the specified port
        """
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", port=self.port)
        await site.start()

        self.logger.info(f"Health check serving on http://127.0.0.1:{self.port}/health")

    def set_state_warm_up(self):
        """
        Set the service state to 'Warming up'
        """
        self.service_state = State.WARMUP

    def set_state_working(self):
        """
        Set the service state to 'Working'
        """
        self.service_state = State.WORK

    def set_state_shut_down(self):
        """
        Set the service state to 'Shutting down'
        """
        self.service_state = State.SHUTDOWN

    def set_state_no_info(self):
        """
        Set the service state to 'No information'
        """
        self.service_state = State.NOINFO
