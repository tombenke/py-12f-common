==========================
A bare-minimum application
==========================

This example introduces a bare-minimum application made, using the py-12f-common package.

The application can be found in the 
`examples/minimum/ folder <https://github.com/tombenke/py-12f-common/tree/master/examples/minimum>`_
in the project's github repository.

The source code
---------------

It is a single-file application. The source code is structured on the following way:

The firs part contain the package imports,
and the definition of the configuration object of the application:

.. code-block:: python

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
    ]

    application_config = Config(APP_NAME, APP_DESCRIPTION, config_entries)

The configuration object defines two choices-type parameters: ``LOG_LEVEL`` and ``LOG_FORMAT``
and ``DUMP_CONFIG`` that is a boolean type parameter.

The choices-type parameters uses the  ``get_level_choices()`` and  ``get_format_choices()`` functions
imported from the ``common.logger`` module to define the selectable values for the command-line arguments.

The second part defines a very simple ``Application`` class, that implements the ``start()`` and ``stop()``
functions, that actually do nothing, but write out some log messages:

.. code-block:: python

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


The final section of the application uses the ``application_entrypoint()`` function
of the ``common.app`` module, that parses the command-line arguments and start the application.

.. code-block:: python

    def main():
        """The main entry point of the application"""
        application_entrypoint(Application, application_config)


    if __name__ == "__main__":
        main()

Usage
-----

Start the application, to get help:

.. code-block:: console

    m$ python main.py  --help
    usage: minimum [-h] [-l {critical,error,warning,success,info,debug,trace}] [-f {text,json}] [-d]

    The bare-minimum application

    optional arguments:
      -h, --help            show this help message and exit
      -l {critical,error,warning,success,info,debug,trace}, --log-level {critical,error,warning,success,info,debug,trace}
                            Log level ['critical', 'error', 'warning', 'success', 'info', 'debug', 'trace']
      -f {text,json}, --log-format {text,json}
                            The format of the log messages ['text', 'json']
      -d, --dump-config     Dump the actual configuration parameters of the application


Start the application at ``debug`` log-level, and ask to dump the config parameters:

.. code-block:: console

    $ python main.py  -d -l debug

    Config:
      LOG_LEVEL: 'debug'
      LOG_FORMAT: 'text'
      DUMP_CONFIG: 'True'
    2022-02-04 21:08:06.288 | INFO     | __main__:start:46 - app starts
    2022-02-04 21:08:06.289 | INFO     | common.app.app_base:run:116 - Application.run: entering wait loop
    2022-02-04 21:08:06.289 | DEBUG    | common.app.app_base:jobs:74 - ApplicationBase.jobs() is called

The application starts at debug log level.
First it dumps the actual config parameters, then executes the ``start`` function.
Next it executes the ``Application.jobs()`` member function, then waits.

Now press the ``Ctrl+C`` keys:

.. code-block:: console

    ^C2022-02-04 21:10:36.241 | INFO     | common.app.signals:fun:27 - signal: 2, frame: <frame at 0xc979b0, file '/usr/lib/python3.8/selectors.py', line 468, code select>
    2022-02-04 21:10:36.241 | INFO     | common.app.app_terminate:terminate:20 - Terminate the application
    2022-02-04 21:10:36.243 | INFO     | __main__:stop:50 - app shuts down
    2022-02-04 21:10:36.244 | INFO     | common.app.app_base:_cancel_all_tasks:279 - Application._cancel_all_tasks: cancelling 1 tasks ...
    2022-02-04 21:10:36.245 | INFO     | common.app.app_base:_stop:251 - Application._stop: closing event loop

The application calls the ``stop()`` function and exits.

