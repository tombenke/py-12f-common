"""Test the config module"""
import os
import unittest
from common.logger.logger import get_format_choices, get_level_choices
from common.config import Config, ConfigEntry, CliEntry

# The expected values for parameters used via env and/or CLI parameter
test_set = dict(
    LOG_LEVEL="debug",
    LOG_FORMAT="text",
    NO_SHORT_FLAG="no_short_flag",
)

APP_NAME = "an-application"
APP_DESCRIPTION = """The description of the application..."""

config_entries = [
    ConfigEntry(
        name="LOG_LEVEL",
        help_text=f"Log level {get_level_choices()}",
        default="info",
        cli=CliEntry(short_flag="-l", name="--log-level", choices=get_level_choices()),
    ),
    ConfigEntry(
        name="LOG_FORMAT",
        help_text=f"The format of the log messages {get_format_choices()}",
        default="text",
        cli=CliEntry(
            short_flag="-f", name="--log-format", choices=get_format_choices()
        ),
    ),
    ConfigEntry(
        name="NO_SHORT_FLAG",
        help_text="No short flag for this parameter",
        default="text",
        cli=CliEntry(short_flag=None, name="--no-short-flag"),
    ),
]


def assert_with_defaults(test_case, config):
    """Assert the config parameters against the default values"""
    print("\nassert with defaults")
    for config_entry in config_entries:
        test_case.assertEqual(config.__dict__[config_entry.name], config_entry.default)


def assert_with_expected(test_case, config, ref):
    """Assert the config parameters against the expected values"""
    for prop_name in ref:
        test_case.assertEqual(config.__dict__[prop_name], ref[prop_name])


class ConfigTestCase(unittest.TestCase):
    "The config test cases"

    def test_config_via_apply_parameters(self) -> None:
        """Test the apply_parameters to config"""
        config = Config(APP_NAME, APP_DESCRIPTION, config_entries)
        config.apply_parameters(test_set)
        assert_with_expected(self, config, test_set)

    def test_config_default_and_via_env(self) -> None:
        """Test the config via env variables"""

        # The configuration object is usually a module-level singleton
        config = Config(APP_NAME, APP_DESCRIPTION, config_entries)
        assert_with_defaults(self, config)

        # setup the environment
        os.environ.update(test_set)
        config = Config(APP_NAME, APP_DESCRIPTION, config_entries)
        assert_with_expected(self, config, test_set)

    def test_config_via_argv(self) -> None:
        """Test the config via parsing the CLI arguments"""
        config = Config(APP_NAME, APP_DESCRIPTION, config_entries)
        config.apply_cli_args(
            [
                "-l",
                test_set["LOG_LEVEL"],
                "-f",
                test_set["LOG_FORMAT"],
                "--no-short-flag",
                test_set["NO_SHORT_FLAG"],
            ]
        )
        assert_with_expected(self, config, test_set)
