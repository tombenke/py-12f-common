"""
This sub-module holds the classes for the configuration management.

The ``Config`` class plays the central role. It uses az array of ``ConfigEntry`` instances to
define the list of config parameters, incl. their names and default values.
Each ``ConfigEntry`` has its own ``CliEntry`` property, which describes the command-line related
counterparts of the config parameters.

This module is responsible for giving default values to the config parameters,
evaulate the environment variables and command-line parameters, and applies them to the config variables.

The precedence is the following, in ascending order (command-line is the strongest):
- default value,
- environment variable,
- command-line parameter.

"""
import argparse
import os
import re
import json
import dotenv


def json_string(string):
    """
    Converts a JSON format string to Python value.
    Can be used as `entry_type` parameter of the `CliEntry` object.
    """
    return json.loads(string)


class CliEntry:
    """
    It is the command-line entry descriptor data-class.

    It holds the details of a ConfigEntry about how to setup the command-line arg parser.

    NOTE: The properties hold by this class are strongly related to
    the `argparse <https://docs.python.org/3/library/argparse.html>`_ package.

    Example:

    .. highlight:: python
    .. code-block:: python

        cli_entry = CliEntry(
            short_flag="-d",
            name="--dump-config",
            entry_type=bool,
            action="store_true")
    """

    short_flag: str
    """Defines the short name of an optional CLI argument, for example: ``-f``"""

    name: str
    """Defines the name of an optional command-line argument, for example: ``--file-name``"""

    entry_type: type
    """
    The type of the argument, e.g. ``int``, ``float``.
    See also: `the argparse docs / type <https://docs.python.org/3/library/argparse.html#type>`_
    """

    action: str
    """
    It specifies how the command-line argument should be handled.
    See also: `the argparse docs / action <https://docs.python.org/3/library/argparse.html#action>`_
    """

    choices: list
    """The list of possible choices, in case the value can be chosen from a predefined set."""

    def __init__(
        self, short_flag=None, name=None, entry_type=str, action="store", choices=None
    ):
        self.short_flag = short_flag
        self.name = name
        self.entry_type = entry_type
        self.action = action
        self.choices = choices

    def __iter__(self):
        """
        Return with an iterable collection of the object properties
        """
        return iter(self.__dict__)

    def __str__(self):
        """
        Returns the object in string format
        """
        return (
            f'CliEntry(short_flag="{self.short_flag}", '
            'name="{self.name}", '
            "entry_type={self.entry_type}, "
            'action="{self.action}", '
            "choices={self.choices})"
        )


class ConfigEntry:
    """
    Config parameter descriptor data-class

    Example:

    .. highlight:: python
    .. code-block:: python

        ConfigEntry(
            name="LOG_LEVEL",
            help_text=f"Log level {get_level_choices()}",
            default="info",
            cli=CliEntry(short_flag="-l", name="--log-level", choices=get_level_choices()),
        )"""

    name: str
    """
    The name of the config parameter.

    Usually this is the name of the environment variable may be used accompanied with the command-line parameter.
    It should be ALL-CAPS.
    """

    help_text: str
    """
    The short description of the config parameter, that will be displayed to the console
    when the ``--help`` switch is used for the application.
    """

    default: str
    """
    The default value of the config parameter.

    The config parameter always has default value, that can be overwritten either by the value of the
    environment variable with the same name, if exists and/or the command-line parameter.
    """

    cli: CliEntry
    """
    The definition of the command-line argument entry, if there is any.

    If given, it defines the hints of the command-line optional argument counterpart of the config parameter.
    Before parsing of the command line parameters, each parameter will be initialized with the actual value
    of the corresponding config parameter, using the built-in default value, then applying the environment variable.
    """

    def __init__(self, name=None, help_text="", default=None, cli=None):
        self.name = name
        self.help_text = help_text
        self.default = default
        self.cli = cli

    def __iter__(self):
        """
        Return with an iterable collection of the object properties
        """
        return iter(self.__dict__)

    def __str__(self):
        """
        Returns the object in string format
        """
        return f'ConfigEntry(name="{self.name}", help_text="{self.help_text}", default="{self.default}", cli={self.cli})'


class Config:
    """
    Configuration class that represent the actual config parameter set of the application.
    The class provides method for resolving the config parameters
    from env variables as well as from CLI parameters.
    """

    def __init__(self, app_name, app_description, config_entries):
        """
        Constructor for the application config.

        :param str app_name: The name of the application.

        :param str app_description: The short description of the application.

        :param Array[ConfigEntry] config_entries: The array of the definitions of config entries.

        It fills the object with the properties given by the `config_entries` argument.
        It also sets the initial value of each parameter from the environment, if it is found
        or set to its default value if the corresponding environment var is missing.
        """
        self.app_name = app_name
        self.app_description = app_description
        self.config_entries = config_entries

        # Load environment variables from .env if exists
        dotenv.load_dotenv(".env")

        for config_entry in config_entries:
            self.__dict__[config_entry.name] = os.environ.get(
                config_entry.name, config_entry.default
            )

    def apply_parameters(self, parameters):
        """
        Overwrites the actual values of the configuration properties with the values given by the
        `parameters` dictionary. Typical usage is, when the CLI argument parser wants to overwrite
        the default, or environment values.

        :param dict parameters: The dictionary of parameters, that have to be applied to the actual set of
            configuration parameters.
            The keys in the ``parameters`` must fit to the names in the configuration object.
        """
        for k in parameters:
            self.__dict__[k] = parameters[k]

    def apply_cli_args(self, argv):
        """
        Take the actual CLI parameters according to the definitions in `self.config_entries`
        parse them, and apply them to the actual properties of the config object.

        :param Array[str] argv: The command line parameters.
        """
        args = self.get_the_cli_args(argv)
        self.apply_parameters(args)

    def get(self, name):
        """
        Get the value of a config parameter by its name.

        :param str name: The name of the config parameter

        :return: The value of the config parameter found, or ``None``, if not found.
        """
        if name in self.__dict__:
            return self.__dict__[name]

        return None

    def get_the_cli_args(self, argv):
        """
        Parse the CLI parameters, and returns with them as a dictionary

        :param Array[str] argv: The command-line parameters
        """
        parser = argparse.ArgumentParser(
            prog=self.app_name, description=self.app_description
        )

        # Build the CLI args parser
        for config_entry in self.config_entries:
            name = config_entry.name
            help_text = config_entry.help_text
            cli = config_entry.cli
            default = self.__dict__[name]

            if cli is not None:
                short_flag = cli.short_flag
                name = cli.name
                entry_type = cli.entry_type
                action = cli.action
                choices = cli.choices

                if action in ["store_false", "store_true"]:
                    # It is a boolean flag
                    if short_flag is None:
                        parser.add_argument(
                            name, help=help_text, default=default, action=action
                        )
                    else:
                        parser.add_argument(
                            short_flag,
                            name,
                            help=help_text,
                            default=default,
                            action=action,
                        )
                else:
                    if short_flag is None:
                        if choices is not None:
                            # It is a selection from the list of choices
                            parser.add_argument(
                                name,
                                type=entry_type,
                                help=help_text,
                                default=default,
                                action=action,
                                choices=choices,
                            )
                        else:
                            # It is a normal flag or positional parameter
                            parser.add_argument(
                                name,
                                type=entry_type,
                                help=help_text,
                                default=default,
                                action=action,
                            )
                    else:
                        if choices is not None:
                            # It is a selection from the list of choices
                            parser.add_argument(
                                short_flag,
                                name,
                                type=entry_type,
                                help=help_text,
                                default=default,
                                action=action,
                                choices=choices,
                            )
                        else:
                            # It is a normal flag or positional parameter
                            parser.add_argument(
                                short_flag,
                                name,
                                type=entry_type,
                                help=help_text,
                                default=default,
                                action=action,
                            )

        # Parse the CLI args
        args = vars(parser.parse_args(argv))

        # Build a dictionary of actual CLI arg values, using the original parameter name
        results = {}
        for config_entry in self.config_entries:
            # Take the original entry name
            entry_name = config_entry.name
            cli = config_entry.cli

            if cli is not None:
                # Take the parameter value of the CLI arg
                name = re.sub(r"^--", "", cli.name).replace("-", "_")

                # Add the value to the results with the original name
                results[entry_name] = args[name]

        return results

    def dump(self):
        """
        Prints the actual values of the config parameters to the console
        """
        print("\nConfig:")
        for config_entry in self.config_entries:
            name = config_entry.name
            value = self.__dict__[name]
            value_type = type(value)
            if value_type == str:
                print(f'  {name}: "{value}" {value_type}')
            else:
                print(f"  {name}: {value} {value_type}")

    def __str__(self):
        """
        Returns with the string representation of the object
        """
        str_repr = ""
        for key, value in self.__dict__.items():
            str_repr += f"{key}='{value}', "

        return str_repr
