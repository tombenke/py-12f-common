"""The application base class"""
from abc import ABC, abstractmethod
import asyncio
from typing import Dict, Optional, Any
from ..logger.logger import init_logger
from .signals import DelayedKeyboardInterrupt


class ApplicationBase(ABC):
    """
    The ApplicationBase class
    """

    def __init__(self, config):
        """
        Initializes the new application object
        """
        self._loop = None  # type: Optional[asyncio.AbstractEventLoop]
        self._wait_event = None  # type: Optional[asyncio.Event]
        self._wait_task = None  # type: Optional[asyncio.Task]
        self.logger = init_logger(config.LOG_LEVEL, config.LOG_FORMAT)
        self.config = config

    def run(self):
        """
        Run the application
        """
        self._loop = asyncio.new_event_loop()

        try:
            # Shield start() from termination.
            try:
                with DelayedKeyboardInterrupt(self.logger):
                    self._start()
            # If there was an attempt to terminate the application,
            # the KeyboardInterrupt is raised AFTER the _start() finishes its job.
            #
            # In that case, the KeyboardInterrupt is re-raised and caught in
            # exception handler below and _stop() is called to clean all resources.
            #
            # Note that it might be generally unsafe to call stop() methods
            # on objects that are not started properly.
            # This is the main reason why the whole execution of _start()
            # is shielded.

            except KeyboardInterrupt:
                self.logger.info("Application.run: got KeyboardInterrupt during start")
                raise

            # Application is started now and is running.
            # Wait for a termination event infinitelly.

            self.logger.info("Application.run: entering wait loop")
            self._wait()
            self.logger.info("Application.run: exiting wait loop")

        except KeyboardInterrupt:
            # The stop() is also shielded from termination.
            try:
                with DelayedKeyboardInterrupt(self.logger):
                    self._stop()
            except KeyboardInterrupt:
                self.logger.info("Application.run: got KeyboardInterrupt during stop")

    @abstractmethod
    async def start(self):
        """Starts the application"""

    @abstractmethod
    async def stop(self):
        """Shuts down the application"""

    async def wait(self):
        """
        Wait until the application got stop signal
        """
        self._wait_event = asyncio.Event()
        self._wait_task = asyncio.create_task(self._wait_event.wait())
        await self._wait_task

    def _start(self):
        self._loop.run_until_complete(self.start())

    def _stop(self):
        self._loop.run_until_complete(self.stop())

        # Because we want clean exit, we patiently wait for completion
        # of the _wait_task (otherwise this task might get cancelled
        # in the _cancel_all_tasks() method - which wouldn't be a problem,
        # but it would be dirty).
        #
        # The _wait_event & _wait_task might not exist if the application
        # has been terminated before calling _wait(), therefore we have to
        # carefully check for their presence.

        if self._wait_event:
            self._wait_event.set()

        if self._wait_task:
            self._loop.run_until_complete(self._wait_task)

        #
        # Before the loop is finalized, we setup an exception handler that
        # suppresses several nasty exceptions.
        #
        # ConnectionResetError
        # --------------------
        # This exception is sometimes raised on Windows, possibly because of a bug in Python.
        #
        # ref: https://bugs.python.org/issue39010
        #
        # When this exception is raised, the context looks like this:
        # context = {
        #     'message': 'Error on reading from the event loop self pipe',
        #     'exception': ConnectionResetError(
        #         22, 'The I/O operation has been aborted because of either a thread exit or an application request',
        #         None, 995, None
        #       ),
        #     'loop': <ProactorEventLoop running=True closed=False debug=False>
        # }
        #
        # OSError
        # -------
        # This exception is sometimes raised on Windows - usually when application is
        # interrupted early after start.
        #
        # When this exception is raised, the context looks like this:
        # context = {
        #     'message': 'Cancelling an overlapped future failed',
        #     'exception': OSError(9, 'The handle is invalid', None, 6, None),
        #     'future': <_OverlappedFuture pending overlapped=<pending, 0x1d8937601f0>
        #                 cb=[BaseProactorEventLoop._loop_self_reading()]>,
        # }
        #

        def __loop_exception_handler(_, context: Dict[str, Any]):
            if isinstance(context["exception"], ConnectionResetError):
                self.logger.info(
                    "Application._stop.__loop_exception_handler: suppressing ConnectionResetError"
                )
            elif isinstance(context["exception"], OSError):
                self.logger.info(
                    "Application._stop.__loop_exception_handler: suppressing OSError"
                )
            else:
                self.logger.info(
                    f"Application._stop.__loop_exception_handler: unhandled exception: {context}"
                )

        self._loop.set_exception_handler(__loop_exception_handler)

        try:
            # Cancel all remaining uncompleted tasks.
            # We should strive to not make any, but mistakes happen and laziness
            # is also a thing.
            #
            # Generally speaking, cancelling tasks shouldn't do any harm (unless
            # they do...).
            self._cancel_all_tasks()

            # Shutdown all active asynchronous generators.
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
        finally:
            # ... and close the loop.
            self.logger.info("Application._stop: closing event loop")
            self._loop.close()

    def _wait(self):
        self._loop.run_until_complete(self.wait())

    def _cancel_all_tasks(self):
        """
        Cancel all tasks in the loop.

        This method injects an asyncio.CancelledError exception
        into all tasks and lets them handle it.

        Note that after cancellation, the event loop is executed again and
        waits for all tasks to complete the cancellation.  This means that
        if some task contains code similar to this:

        >>> except asyncio.CancelledError:
        >>>     await asyncio.Event().wait()

        ... then the loop doesn't ever finish.
        """

        #
        # Code kindly borrowed from asyncio.run().
        #

        to_cancel = asyncio.tasks.all_tasks(self._loop)
        self.logger.info(
            f"Application._cancel_all_tasks: cancelling {len(to_cancel)} tasks ..."
        )

        if not to_cancel:
            return

        for task in to_cancel:
            task.cancel()

        self._loop.run_until_complete(
            asyncio.tasks.gather(*to_cancel, loop=self._loop, return_exceptions=True)
        )

        for task in to_cancel:
            if task.cancelled():
                continue

            if task.exception() is not None:
                self._loop.call_exception_handler(
                    {
                        "message": "unhandled exception during Application.run() shutdown",
                        "exception": task.exception(),
                        "task": task,
                    }
                )
