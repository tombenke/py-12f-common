"""
This sub-module holds the classes for the configuration management.

The ``Config`` class plays the central role. It uses az array of ``ConfigEntry`` instances to
define the list of config parameters, incl. their names and default values.
Each ``ConfigEntry`` has its own ``CliEntry`` property, which describes the comman-line related
counterparts of the config parameters.

This module is responsible for giving default values to the config parameters,
evaulate the environment variables and command-line parameters, and applies them to the config variables.

The precedence is the following, in ascending order (command-line is the strongest):
- default value,
- environment variable,
- command-line parameter.

"""
import argparse
from dataclasses import dataclass, astuple
import os
import re
import dotenv


@dataclass
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

    entry_type: type = str
    """
    The type of the argument, e.g. ``int``, ``float``.
    See also: `the argparse docs / type <https://docs.python.org/3/library/argparse.html#type>`_
    """

    action: str = "store"
    """
    It specifies how the comman-line argument should be handled.
    See also: `the argparse docs / action <https://docs.python.org/3/library/argparse.html#action>`_
    """

    choices: list = None
    """The list of possible choices, in case the value can be chosen from a predefined set."""

    def __iter__(self):
        """
        Return with an iterable collection of the object properties
        """
        return iter(astuple(self))


@dataclass
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

    help_text: str = ""
    """
    The short description of the config parameter, that will be displayed to the console
    when the ``--help`` switch is used for the application.
    """

    default: str = ""
    """
    The default value of the config parameter.

    The config parameter always has default value, that can be overwritten either by the value of the
    environment variable with the same name, if exists and/or the command-line parameter.
    """

    cli: CliEntry = None
    """
    The definition of the command-line argument entry, if there is any.

    If given, it defines the hints of the command-line optional argument counterpart of the config parameter.
    Before parsing of the command line parameters, each parameter will be initialized with the actual value
    of the corresponding config parameter, using the built-in default value, then applying the environment variable.
    """

    def __iter__(self):
        """
        Return with an iterable collection of the object properties
        """
        return iter(astuple(self))


@dataclass
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
            (name, _, default, _) = config_entry
            self.__dict__[name] = os.environ.get(name, default)

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
            (name, help_text, _, cli) = config_entry
            default = self.__dict__[name]
            if cli is not None:
                (short_flag, name, entry_type, action, choices) = cli
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
            (entry_name, _, _, cli) = config_entry

            if cli is not None:
                # Take the parameter value of the CLI arg
                (_, name_or_flag, _, _, _) = cli
                name = re.sub(r"^--", "", name_or_flag).replace("-", "_")

                # Add the value to the results with the original name
                results[entry_name] = args[name]

        return results

    def dump(self):
        """
        Prints the actual values of the config parameters to the console
        """
        print("\nConfig:")
        for config_entry in self.config_entries:
            (name, _, _, _) = config_entry
            print(f"  {name}: '{self.__dict__[name]}'")

    def __str__(self):
        """
        Returns with the string representation of the object
        """
        str_repr = ""
        for key, value in self.__dict__.items():
            str_repr += f"{key}='{value}', "

        return str_repr
