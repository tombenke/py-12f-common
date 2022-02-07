"""The config module of the application"""
from common.config import Config, ConfigEntry, CliEntry
from common.logger import get_level_choices, get_format_choices

APP_NAME = "minimum"
APP_DESCRIPTION = "The bare-minimum application"

config_entries = [
    ConfigEntry(
        name="NUM_PRODUCERS",
        help_text="The number of producers",
        default=1,
        cli=CliEntry(
            short_flag="-p", name="--num-producers", entry_type=int, action="store"
        ),
    ),
    ConfigEntry(
        name="NUM_CONSUMERS",
        help_text="The number of consumers",
        default=1,
        cli=CliEntry(
            short_flag="-c", name="--num-consumers", entry_type=int, action="store"
        ),
    ),
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
]

application_config = Config(APP_NAME, APP_DESCRIPTION, config_entries)
