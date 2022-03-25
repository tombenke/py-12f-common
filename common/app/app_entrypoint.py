"""
The boilerplate implementation of an application
"""
import sys
from common.config import Config


def application_entrypoint(application_class, config: Config, argv=None):
    """
    The main entry point of the application.

    This is a built-in implementation of a typical application.

    :param application_class: The type of the Application class,
        that origins from the ``ApplicationBase``.

    :param Config config: the default configuration object, with environment values applied to it.

    :param Array argv: The array of CLI arguments. If not defined or ``None``,
        then the ``sys.argv[1:]`` will be used instead.

    Example of usage:

    .. highlight:: python
    .. code-block:: python

        #!/usr/bin/env python
        # -*- coding: utf-8 -*-
        '''The main entry-point of the application.'''
        from common.app import application_entrypoint
        from config import config
        from app import Application


        def main():
            '''The main entry point of the application'''
            application_entrypoint(Application, config)


        if __name__ == "__main__":
            main()
    """
    # Parses the CLI arguments, and merge them into the configuration
    if argv is None:
        config.apply_cli_args(sys.argv[1:])
    else:
        config.apply_cli_args(argv)

    if config.get("DUMP_CONFIG"):
        config.dump()

    # Create an application instance
    app = application_class(config)

    # Run the application until a shutdown signal arrives
    app.run()
