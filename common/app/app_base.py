"""
The application base class [1]_.

.. [1] The KeyboardInterrupt handling, and signal handler shadowing is implemented based on the
   `Holy grail of graceful shutdown in Python <https://github.com/wbenny/python-graceful-shutdown>`_.
   Credits to `Petr Beneš (wbenny) <https://github.com/wbenny>`_.
"""
from abc import ABC, abstractmethod
import asyncio
from ..logger.logger import init_logger
from .signals import DelayedKeyboardInterrupt, add_term_signal_handler
from .app_terminate import terminate


class ApplicationBase(ABC):
    """
    Abstract base class for applications [1]_.

    It is responsible for

    - storing the configuration,
    - setting up the central logger,
    - starting internal services,
    - keep running until graceful shut-down (caused by a termination signal, or internal error),
    - stop the internal services when shuts down.

    When you create a new instance of a derived application class, you are handing over the actual
    deployment-dependent configuration to it.
    The constructor of the base class stores this config, as well as it initializes the logger,
    according to the configuration's ``LOG_LEVEL`` and ``LOG_FORMAT`` properties.

    Applications that are subclass of this base class must implement two ``async`` member functions:
    ``start()`` and ``stop()``.
    The ``start()`` will be called by the ``run()`` function, when the application starts running.
    You can put those operations here, for example, that initializes resources, open database connections, etc.
    The ``stop()`` will be called, when the application is shutting down. This is, where you can put
    those operations that needs to be executed, before the application exits, e.g. closing database
    connections.

    After creating the application class, you only need to call the ``run()`` member function,
    then the application will start running, calls the ``start()`` function
    and enters into its internal ``wait()`` function, which is waiting for a termination signal.

    The ``wait()`` function also keep running those asynchronous tasks, that were created via
    the ``start()`` function.

    It is also possible to run some extra jobs, because the ``ApplicationBase`` will call
    its ``async jobs()`` function before it enters its wait function.
    The default implementation of ``jobs()`` is empty. You can overload it with your implementation.
    It is also possible to execute the ``terminate()`` function at the end of the ``jobs()`` function,
    then the application will automatically shuts down, after finished the jobs.
    """

    def __init__(self, config):
        """
        Initializes the new application object.

        :param Config config: the configuration object of the overall application.

        It creates an internal event-loop, that will be used to create and run the application's
        internal services, tasks.
        """
        self._loop = None
        self._wait_event = None
        self._wait_task = None
        self.logger = init_logger(config.get("LOG_LEVEL"), config.get("LOG_FORMAT"))
        self.config = config

    async def jobs(self):
        """
        The subclasses can place here their jobs, that run after start() finished.
        """
        self.logger.debug("ApplicationBase.jobs() is called")

    def run(self):
        """
        Runs the application according to the following steps:

        1. Starts the internal services, defined by the ``start()`` member function.
        2. Executes the ``jobs()`` member function.
        3. Enters the internal event processing execution loop, and wait until either a
           an unhandled interruption occur, or the application receives a signal for stopping.
        4. Shuts down the internal services according to the implementation of the ``stop()`` function.
        5. Exits.
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

            def signal_cb():
                terminate()

            add_term_signal_handler(self.logger, signal_cb)

            # Application is started now and is running.
            # Wait for a termination event infinitely.
            self.logger.info("Application.run: entering wait loop")
            self._wait()
            self.logger.info("Application.run: exiting wait loop")

        # Any unhandled exception occures, the application will terminate
        except BaseException:
            # The stop() is also shielded from termination.
            try:
                with DelayedKeyboardInterrupt(self.logger):
                    self._stop()
            except KeyboardInterrupt:
                self.logger.info("Application.run: got KeyboardInterrupt during stop")

    @abstractmethod
    async def start(self):
        """
        Starts the application

        This function will be called by the ``run()`` function, when the application starts running.
        You can put those operations here, for example, that initializes resources,
        open database connections, starts tasks, etc.

        This is an abstract member function that the subclass of ApplicationBase class must implement.
        """

    @abstractmethod
    async def stop(self):
        """
        Shuts down the application

        It will be called, when the application is shutting down.
        This is, where you can put those operations that needs to be executed,
        before the application exits, e.g. closing database connections.

        This is an abstract member function that the subclass of ApplicationBase class must implement.
        """

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

        def __loop_exception_handler(_, context):
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

    async def wait(self):
        """
        Wait until the application got stop signal
        """
        self._wait_event = asyncio.Event()
        self._wait_task = asyncio.create_task(self._wait_event.wait())
        await asyncio.gather(self.jobs(), self._wait_task)
        # await self._wait_task

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
