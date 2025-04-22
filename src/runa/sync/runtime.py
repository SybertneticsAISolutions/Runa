"""
Runtime support for asynchronous programming in Runa.
This module provides utility functions and classes for async operations.
"""
import asyncio
import inspect
import functools


class AsyncSupport:
    """Support class for async operations in Runa."""

    @staticmethod
    def run_async(coro):
        """
        Run an asynchronous coroutine and return its result.

        This is used when an async function is called from synchronous code.
        """
        loop = AsyncSupport.get_or_create_event_loop()
        return loop.run_until_complete(coro)

    @staticmethod
    def get_or_create_event_loop():
        """Get the current event loop or create a new one if necessary."""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            # No event loop in current thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    @staticmethod
    def is_async_context():
        """Check if the current context is asynchronous."""
        try:
            return inspect.currentframe().f_back.f_locals.get('__awaitable__', False)
        except (AttributeError, ValueError):
            return False

    @staticmethod
    async def async_map(func, iterable):
        """
        Asynchronously map a function over an iterable.

        If the function is sync, it will be executed in parallel using the thread pool.
        If the function is async, it will be awaited directly.
        """
        if inspect.iscoroutinefunction(func):
            # Async function - gather all coroutines
            coros = [func(item) for item in iterable]
            return await asyncio.gather(*coros)
        else:
            # Sync function - run in parallel using thread pool
            loop = asyncio.get_event_loop()
            return await asyncio.gather(*[
                loop.run_in_executor(None, functools.partial(func, item))
                for item in iterable
            ])

    @staticmethod
    async def async_filter(func, iterable):
        """
        Asynchronously filter items from an iterable.

        If the function is sync, it will be executed in parallel using the thread pool.
        If the function is async, it will be awaited directly.
        """
        if inspect.iscoroutinefunction(func):
            # Async function - gather all coroutines
            coros = [func(item) for item in iterable]
            results = await asyncio.gather(*coros)
        else:
            # Sync function - run in parallel using thread pool
            loop = asyncio.get_event_loop()
            results = await asyncio.gather(*[
                loop.run_in_executor(None, functools.partial(func, item))
                for item in iterable
            ])

        # Filter items based on results
        return [item for item, result in zip(iterable, results) if result]

    @staticmethod
    async def async_reduce(func, iterable, initializer=None):
        """
        Asynchronously reduce an iterable using a function.

        If the function is sync, it will be executed sequentially.
        If the function is async, it will be awaited for each step.
        """
        it = iter(iterable)

        if initializer is None:
            try:
                value = next(it)
            except StopIteration:
                raise TypeError("async_reduce() of empty sequence with no initial value")
        else:
            value = initializer

        if inspect.iscoroutinefunction(func):
            # Async function - await each step
            for item in it:
                value = await func(value, item)
        else:
            # Sync function - execute sequentially
            for item in it:
                value = func(value, item)

        return value


# Export utility functions for Runa runtime
run_async = AsyncSupport.run_async
async_map = AsyncSupport.async_map
async_filter = AsyncSupport.async_filter
async_reduce = AsyncSupport.async_reduce