"""Test the config module"""
import os
import unittest
from common.logger.logger import get_format_choices, get_level_choices
from common.config import Config, ConfigEntry, CliEntry, json_string

# The expected values for parameters used via env and/or CLI parameter
test_set_input = dict(
    LOG_LEVEL="debug",
    LOG_FORMAT="text",
    INTEGER="55",
    FLOAT="3.1415",
    JSON_STRING_ARRAY='["first","second","third"]',
    JSON_OBJECT='{"id": 42,"label":"The Universe"}',
)

# The expected values after parsing the parameters
test_set_expected = dict(
    LOG_LEVEL="debug",
    LOG_FORMAT="text",
    INTEGER=55,
    FLOAT=3.1415,
    NO_SHORT_FLAG=False,
    DUMP_CONFIG=True,
    JSON_STRING_ARRAY=["first", "second", "third"],
    JSON_OBJECT={"id": 42, "label": "The Universe"},
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
        default="False",
        cli=CliEntry(
            short_flag=None,
            name="--no-short-flag",
            entry_type=bool,
            action="store_false",
        ),
    ),
    ConfigEntry(
        name="DUMP_CONFIG",
        help_text="Dump the actual configuration parameters of the application",
        default="False",
        cli=CliEntry(
            # short_flag="-d",
            short_flag=None,
            name="--dump-config",
            entry_type=bool,
            action="store_true",
        ),
    ),
    ConfigEntry(
        name="INTEGER",
        help_text="An integer number",
        default="0",
        cli=CliEntry(short_flag="-i", name="--integer", entry_type=int),
    ),
    ConfigEntry(
        name="FLOAT",
        help_text="A float number",
        default="0.",
        cli=CliEntry(short_flag="-r", name="--float", entry_type=float),
    ),
    ConfigEntry(
        name="JSON_STRING_ARRAY",
        help_text="This is a JSON format array or strings",
        default='["first", "second", "third"]',
        cli=CliEntry(
            short_flag=None, name="--json-string-array", entry_type=json_string
        ),
    ),
    ConfigEntry(
        name="JSON_OBJECT",
        help_text="This is a JSON format object",
        default="{}",
        cli=CliEntry(short_flag=None, name="--json-object", entry_type=json_string),
    ),
]


def assert_with_defaults(test_case, config):
    """Assert the config parameters against the default values"""
    for config_entry in config_entries:
        test_case.assertEqual(config.__dict__[config_entry.name], config_entry.default)


def assert_with_expected(test_case, config, ref):
    """Assert the config parameters against the expected values"""
    for prop_name in ref:
        test_case.assertEqual(config.__dict__[prop_name], ref[prop_name])


class ConfigTestCase(unittest.TestCase):
    """The config test cases"""

    def test_config_via_apply_parameters(self) -> None:
        """Test the apply_parameters to config"""
        config = Config(APP_NAME, APP_DESCRIPTION, config_entries)
        config.apply_parameters(test_set_expected)
        assert_with_expected(self, config, test_set_expected)

    def test_config_default_and_via_env(self) -> None:
        """Test the config via env variables"""

        # The configuration object is usually a module-level singleton
        config = Config(APP_NAME, APP_DESCRIPTION, config_entries)
        assert_with_defaults(self, config)

        # setup the environment
        os.environ.update(test_set_input)
        config = Config(APP_NAME, APP_DESCRIPTION, config_entries)
        assert_with_expected(self, config, test_set_input)

    def test_config_via_argv(self) -> None:
        """Test the config via parsing the CLI arguments"""
        config = Config(APP_NAME, APP_DESCRIPTION, config_entries)
        config.apply_cli_args(
            [
                "-l",
                test_set_input["LOG_LEVEL"],
                "-f",
                test_set_input["LOG_FORMAT"],
                "--dump-config",
                "--no-short-flag",
                "-i",
                test_set_input["INTEGER"],
                "-r",
                test_set_input["FLOAT"],
                "--json-string",
                test_set_input["JSON_STRING_ARRAY"],
            ]
        )
        assert_with_expected(self, config, test_set_expected)
        config.dump()
        print(f"\nconfig: {config}")
