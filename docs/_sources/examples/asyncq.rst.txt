================================
An application using async queue
================================

This application implements a ``jobs()`` function,
in which it uses producer-consumer tasks communicating via async queue with each other.

The application can be found in the 
`examples/minimum/ folder <https://github.com/tombenke/py-12f-common/tree/master/examples/asyncq>`_
in the project's github repository.

The source code
---------------

The configuration is in the ``config.py`` file:

.. code-block:: python

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

The implementation of the ``Application`` class is placed into the ``application.py`` file:

.. code-block:: python

    """The application module"""
    import asyncio
    import itertools as it
    import os
    import random
    import time
    from common.app import ApplicationBase, terminate


    async def makeitem(size: int = 5) -> str:
        """Make a random, hex value to be a payload"""
        return os.urandom(size).hex()


    async def randsleep(logger, caller=None) -> None:
        """Makes the caller to sleep for a randomly selected period between 1-3 seconds"""
        i = random.randint(1, 3)
        if caller:
            logger.info(f"{caller} sleeping for {i} seconds.")
        await asyncio.sleep(i)


    async def produce(logger, name: int, queue: asyncio.Queue) -> None:
        """Send randomly generated payloads into the `queue` randomly selected times between 1-5"""
        num = random.randint(1, 5)
        for _ in it.repeat(None, num):  # Synchronous loop for each single producer
            await randsleep(logger, caller=f"Producer {name}")
            item = await makeitem()
            perf_counter = time.perf_counter()
            await queue.put((item, perf_counter))
            logger.info(f"Producer {name} added <{item}> to queue.")


    async def consume(logger, name: int, queue: asyncio.Queue) -> None:
        """Consumes the"""
        while True:
            await randsleep(logger, caller=f"Consumer {name}")
            item, perf_counter = await queue.get()
            now = time.perf_counter()
            logger.info(
                f"Consumer {name} got element <{item}>"
                f" in {now-perf_counter:0.5f} seconds."
            )
            queue.task_done()


    class Application(ApplicationBase):
        """
        The Application class
        """

        started = None

        async def start(self):
            """
            Starts the application.
            """
            self.logger.info("app starts")
            self.started = time.perf_counter()

        async def stop(self):
            """
            Shuts down the application

            """
            self.logger.info("app shuts down")

            elapsed = time.perf_counter() - self.started
            self.logger.info(f"Program completed in {elapsed:0.5f} seconds.")

        async def jobs(self):
            """
            Jobs definition of the application.

            It will create producers and consumers, that will communicate with each other via an async queue.
            The producers will randomly select how many messages will send, with how long delay among the sendings.

            This will run the producers, until they finish their work,
            waits until the queue will be empty, then closes the consumers, finally it terminates.
            """

            # Create the async queue for communication
            queue = asyncio.Queue()

            # Takes the command-line parameters to determine the number of producers and consumers
            nprod = self.config.get("NUM_PRODUCERS")
            ncon = self.config.get("NUM_CONSUMERS")
            self.logger.info(f"jobs started with {nprod} producers and {ncon} consumers.")

            # Create the `nprod` number of producer and `ncon` number of consumer tasks
            producers = [
                asyncio.create_task(produce(self.logger, num, queue))
                for num in range(nprod)
            ]
            consumers = [
                asyncio.create_task(consume(self.logger, num, queue)) for num in range(ncon)
            ]

            # Make the tasks running
            await asyncio.gather(*producers)

            # Implicitly awaits consumers
            await queue.join()

            # Stops the consumers
            for consumer in consumers:
                consumer.cancel()

            # Terminate the application, the `stop()` will take care for closing the consumers
            self.logger.info("jobs finished")
            terminate()

The main entrypoint of the allplication is in the ``main.py`` file and it is this simple:

.. code-block:: python

    """Producer-consumer tasks communicating via async queue."""
    from common.app import application_entrypoint
    from common.examples.asyncq import Application, application_config


    def main():
        """The main entry point of the application"""
        application_entrypoint(Application, application_config)


    if __name__ == "__main__":
        main()

Usage
-----

Start the application with some parameters:

.. code-block:: console

    $ python ./main.py -p 2 -c 3
    2022-02-07 16:06:21.057 | INFO     | common.examples.asyncq.application:start:55 - app starts
    2022-02-07 16:06:21.058 | INFO     | common.app.app_base:run:116 - Application.run: entering wait loop
    2022-02-07 16:06:21.058 | INFO     | common.examples.asyncq.application:jobs:85 - jobs started with 2 producers and 3 consumers.
    2022-02-07 16:06:21.058 | INFO     | common.examples.asyncq.application:randsleep:19 - Producer 0 sleeping for 2 seconds.
    2022-02-07 16:06:21.058 | INFO     | common.examples.asyncq.application:randsleep:19 - Producer 1 sleeping for 3 seconds.
    2022-02-07 16:06:21.058 | INFO     | common.examples.asyncq.application:randsleep:19 - Consumer 0 sleeping for 3 seconds.
    2022-02-07 16:06:21.059 | INFO     | common.examples.asyncq.application:randsleep:19 - Consumer 1 sleeping for 2 seconds.
    2022-02-07 16:06:21.059 | INFO     | common.examples.asyncq.application:randsleep:19 - Consumer 2 sleeping for 2 seconds.
    2022-02-07 16:06:23.061 | INFO     | common.examples.asyncq.application:produce:31 - Producer 0 added <4f3ae37c38> to queue.
    2022-02-07 16:06:23.062 | INFO     | common.examples.asyncq.application:consume:40 - Consumer 1 got element <4f3ae37c38> in 0.00161 seconds.
    2022-02-07 16:06:23.063 | INFO     | common.examples.asyncq.application:randsleep:19 - Consumer 1 sleeping for 2 seconds.
    2022-02-07 16:06:24.060 | INFO     | common.examples.asyncq.application:produce:31 - Producer 1 added <2cbdbcab85> to queue.
    2022-02-07 16:06:24.060 | INFO     | common.examples.asyncq.application:randsleep:19 - Producer 1 sleeping for 3 seconds.
    2022-02-07 16:06:24.061 | INFO     | common.examples.asyncq.application:consume:40 - Consumer 0 got element <2cbdbcab85> in 0.00176 seconds.
    2022-02-07 16:06:24.062 | INFO     | common.examples.asyncq.application:randsleep:19 - Consumer 0 sleeping for 3 seconds.
    2022-02-07 16:06:27.064 | INFO     | common.examples.asyncq.application:produce:31 - Producer 1 added <0a0ae9301d> to queue.
    2022-02-07 16:06:27.065 | INFO     | common.examples.asyncq.application:consume:40 - Consumer 2 got element <0a0ae9301d> in 0.00117 seconds.
    2022-02-07 16:06:27.065 | INFO     | common.examples.asyncq.application:randsleep:19 - Consumer 2 sleeping for 3 seconds.
    2022-02-07 16:06:27.066 | INFO     | common.examples.asyncq.application:jobs:106 - jobs finished
    2022-02-07 16:06:27.066 | INFO     | common.app.app_terminate:terminate:20 - Terminate the application
    2022-02-07 16:06:27.067 | INFO     | common.examples.asyncq.application:stop:63 - app shuts down
    2022-02-07 16:06:27.068 | INFO     | common.examples.asyncq.application:stop:66 - Program completed in 6.01020 seconds.
    2022-02-07 16:06:27.069 | INFO     | common.app.app_base:_cancel_all_tasks:274 - Application._cancel_all_tasks: cancelling 0 tasks ...
    2022-02-07 16:06:27.069 | INFO     | common.app.app_base:_stop:237 - Application._stop: closing event loop

