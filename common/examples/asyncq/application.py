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
