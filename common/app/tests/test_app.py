"""Test the application module"""
import unittest
from common.app import ApplicationBase, application_entrypoint, terminate
from common.config import Config


class TestApplication(ApplicationBase):
    """
    The TestApplication class
    """

    async def start(self):
        """Starts the application, and sets up the internal modules and services"""
        self.logger.info("app starts")

    async def stop(self):
        """Shuts down the application"""
        self.logger.info("app shuts down")

    async def jobs(self):
        """Jobs"""
        self.logger.info("jobs called")
        terminate()


class ApplicationTestCase(unittest.IsolatedAsyncioTestCase):
    "The Application test cases"

    def test_application_start_stop(self) -> None:
        """Test the starting and stopping of an application"""

        app_name = "test-app-name"
        config = Config(app_name, "test-app-description", [])
        self.assertEqual(config.app_name, app_name)
        application_entrypoint(TestApplication, config, argv=[])
