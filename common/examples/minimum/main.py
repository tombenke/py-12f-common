"""
This is a bare-minimum application made, using the py-12f-common package.
"""
from common.app import ApplicationBase, application_entrypoint
from common.config import Config, ConfigEntry, CliEntry
from common.logger import get_level_choices, get_format_choices

APP_NAME = "minimum"
APP_DESCRIPTION = "The bare-minimum application"

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
        name="DUMP_CONFIG",
        help_text="Dump the actual configuration parameters of the application",
        default=False,
        cli=CliEntry(
            short_flag="-d", name="--dump-config", entry_type=bool, action="store_true"
        ),
    ),
    ConfigEntry(
        name="HEALTH_CHECK",
        help_text="Enable to run health check web service with '/health' endpoint",
        default=False,
        cli=CliEntry(
            short_flag="-hc",
            name="--health-check",
            entry_type=bool,
            action="store_true",
        ),
    ),
]

application_config = Config(APP_NAME, APP_DESCRIPTION, config_entries)


class Application(ApplicationBase):
    """
    The Application class
    """

    async def start(self):
        """Starts the application, and sets up the internal modules and services"""
        self.logger.info("app starts")

    async def stop(self):
        """Shuts down the application"""
        self.logger.info("app shuts down")


def main():
    """The main entry point of the application"""
    application_entrypoint(Application, application_config)


if __name__ == "__main__":
    main()
