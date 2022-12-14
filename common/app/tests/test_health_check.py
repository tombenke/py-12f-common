"""Test the application module"""
import unittest
import requests
from common.app import ApplicationBase, application_entrypoint, terminate
from common.config import Config, ConfigEntry, CliEntry
from .exceptions import HealthCheckTestError


def check_response(expected_status_code, expected_notes, response):
    """
    Compare expected and actual status codes and notes from response. Raise a HealthCheckTestError if one of them is
    not equal.
    """
    if expected_status_code != response.status_code:
        raise HealthCheckTestError(
            f"Expected and actual status codes are not equal: {expected_status_code} and {response.status_code}"
        )
    if expected_notes != response.json()["notes"]:
        raise HealthCheckTestError(
            f"Expected and actual notes are not equal: {expected_notes} and {response.json()['notes']}"
        )


class TestApplication(ApplicationBase):
    """
    The TestApplication class
    """

    async def start(self):
        """Starts the application, and sets up the internal modules and services"""
        self.logger.info("app starts")

        # NOINFO initial state
        expected_status_code = 503
        expected_notes = ["No information about the service"]

        future = self._loop.run_in_executor(
            None, requests.get, "http://127.0.0.1:8008/health"
        )
        response = await future

        check_response(expected_status_code, expected_notes, response)
        self.logger.info("1. test case passed")

        # WARMUP state
        self.logger.info("Set service state to WARMUP")
        self.health_check.set_state_warm_up()

        expected_status_code = 202
        expected_notes = ["Service is not healthy, it is warming up or shutting down"]

        future = self._loop.run_in_executor(
            None, requests.get, "http://127.0.0.1:8008/health"
        )
        response = await future

        check_response(expected_status_code, expected_notes, response)
        self.logger.info("2. test case passed")

        # WORK state
        self.logger.info("Set service state to WORK")
        self.health_check.set_state_working()

        expected_status_code = 200
        expected_notes = ["Service is running"]

        future = self._loop.run_in_executor(
            None, requests.get, "http://127.0.0.1:8008/health"
        )
        response = await future

        check_response(expected_status_code, expected_notes, response)
        self.logger.info("3. test case passed")

    async def stop(self):
        """Shuts down the application"""
        self.logger.info("app shuts down")

    async def jobs(self):
        """Jobs"""
        self.logger.info("jobs called")

        # SHUTDOWN state
        self.logger.info("Set service state to SHUTDOWN")
        self.health_check.set_state_shut_down()

        expected_status_code = 202
        expected_notes = ["Service is not healthy, it is warming up or shutting down"]

        future = self._loop.run_in_executor(
            None, requests.get, "http://127.0.0.1:8008/health"
        )
        response = await future

        check_response(expected_status_code, expected_notes, response)
        self.logger.info("4. test case passed")

        terminate()


class ApplicationTestCase(unittest.IsolatedAsyncioTestCase):
    """The Application test cases"""

    def test_application_start_stop(self) -> None:
        """Test the starting and stopping of an application"""

        app_name = "test-app-name"
        config = Config(
            app_name,
            "test-app-description",
            [
                ConfigEntry(
                    name="HEALTH_CHECK",
                    help_text="Enable to run health check web service with '/health' endpoint",
                    default=True,
                    cli=CliEntry(
                        short_flag="-hc",
                        name="--health-check",
                        entry_type=bool,
                        action="store_true",
                    ),
                ),
                ConfigEntry(
                    name="HEALTH_CHECK_HOST",
                    help_text="Host for health check web service",
                    default="127.0.0.1",
                    cli=CliEntry(
                        short_flag="-hh",
                        name="--health-check-host",
                        entry_type=str,
                    ),
                ),
                ConfigEntry(
                    name="HEALTH_CHECK_PORT",
                    help_text="Port number for health check web service",
                    default=8008,
                    cli=CliEntry(
                        short_flag="-hp",
                        name="--health-check-port",
                        entry_type=int,
                    ),
                ),
            ],
        )
        self.assertEqual(config.app_name, app_name)
        application_entrypoint(TestApplication, config, argv=[])
