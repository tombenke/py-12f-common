"""Generic Config related classes"""
import argparse
from dataclasses import dataclass, astuple
import os
import re


@dataclass
class CliEntry:
    """
    Details of a ConfigEntry about how to setup the CLI arg parser
    NOTE: the properties hold by this class are strongly related to
    """

    short_flag: str
    name: str
    entry_type: type = str
    action: str = "store"
    choices: list = None

    def __iter__(self):
        """
        Return with an iterable collection of the object properties
        """
        return iter(astuple(self))


@dataclass
class ConfigEntry:
    """
    Config parameter deswcriptor class
    """

    name: str
    help_text: str = ""
    default: str = ""
    cli: CliEntry = None

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
        Constructor for the application config
        It fills the object with the properties given by the `config_entries` argument.
        It also sets the initial value of each parameter from the environment, if it is found
        or set to its default value if the corresponding environment var is missing.
        """
        self.app_name = app_name
        self.app_description = app_description
        self.config_entries = config_entries

        for config_entry in config_entries:
            (name, _, default, _) = config_entry
            self.__dict__[name] = os.environ.get(name, default)

    def apply_parameters(self, parameters):
        """
        Overwrites the actual values of the configuration properties with the values given by the
        `parameters` dictionary. Typically usage is, when the CLI argument parser wants to overwrite
        the default, or environment values.
        """
        for k in parameters:
            self.__dict__[k] = parameters[k]

    def apply_cli_args(self, argv):
        """
        Take the actual CLI parameters according to the definitions in `self.config_entries`
        parse them, and apply them to the actual properties of the config object.
        """
        args = self.get_the_cli_args(argv)
        self.apply_parameters(args)

    def get_the_cli_args(self, argv):
        """
        Parse the CLI parameters, and returns with them as a dictionary
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
                    parser.add_argument(
                        short_flag, name, help=help_text, default=default, action=action
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
