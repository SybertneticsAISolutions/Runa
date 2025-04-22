"""
Runtime operations for functional programming in Runa.
This module provides utility functions for functional programming features.
"""
import functools
import inspect
import asyncio


def pipeline(value, func):
    """
    Apply a function to a value (pipeline operator implementation).

    Args:
        value: The value to pass to the function
        func: The function to apply

    Returns:
        The result of applying the function to the value
    """
    # Check if the function is async and we're in an async context
    if inspect.iscoroutinefunction(func) and is_async_context():
        # Make a coroutine that we can await
        return func(value)

    # Regular function call
    return func(value)


def partial(func, *args, **kwargs):
    """
    Create a partial application of a function.

    Args:
        func: The function to partially apply
        *args: Positional arguments to fix
        **kwargs: Keyword arguments to fix

    Returns:
        A new function with some arguments fixed
    """
    # Handle async functions specially
    if inspect.iscoroutinefunction(func):
        # Create an async partial function
        @functools.wraps(func)
        async def async_partial(*more_args, **more_kwargs):
            # Combine arguments
            combined_kwargs = kwargs.copy()
            combined_kwargs.update(more_kwargs)
            return await func(*(args + more_args), **combined_kwargs)

        return async_partial

    # Regular partial application
    return functools.partial(func, *args, **kwargs)


def compose(*funcs):
    """
    Compose functions right to left.

    Args:
        *funcs: Functions to compose, applied right to left

    Returns:
        A new function that is the composition of the input functions
    """
    # Check if any function is async
    has_async = any(inspect.iscoroutinefunction(f) for f in funcs)

    if has_async:
        # Create an async composition
        async def async_composed(x):
            for f in reversed(funcs):
                if inspect.iscoroutinefunction(f):
                    x = await f(x)
                else:
                    x = f(x)
            return x

        return async_composed

    # Regular function composition
    def composed(x):
        for f in reversed(funcs):
            x = f(x)
        return x

    return composed


def map_function(func, collection):
    """
    Map a function over a collection.

    Args:
        func: The function to apply to each element
        collection: The collection to map over

    Returns:
        A new collection with the function applied to each element
    """
    # Check if func is async
    if inspect.iscoroutinefunction(func):
        # Return an async generator
        async def async_map():
            return [await func(item) for item in collection]

        # If we're in an async context, return the coroutine
        if is_async_context():
            return async_map()

        # Otherwise, run the coroutine in an event loop
        loop = get_or_create_event_loop()
        return loop.run_until_complete(async_map())

    # Regular map
    return [func(item) for item in collection]


def filter_function(predicate, collection):
    """
    Filter a collection using a predicate function.

    Args:
        predicate: The function to test each element
        collection: The collection to filter

    Returns:
        A new collection with only elements that pass the predicate
    """
    # Check if predicate is async
    if inspect.iscoroutinefunction(predicate):
        # Return an async generator
        async def async_filter():
            result = []
            for item in collection:
                if await predicate(item):
                    result.append(item)
            return result

        # If we're in an async context, return the coroutine
        if is_async_context():
            return async_filter()

        # Otherwise, run the coroutine in an event loop
        loop = get_or_create_event_loop()
        return loop.run_until_complete(async_filter())

    # Regular filter
    return [item for item in collection if predicate(item)]


def reduce_function(func, collection, initial=None):
    """
    Reduce a collection using a function.

    Args:
        func: The function to apply to each element
        collection: The collection to reduce
        initial: The initial value (default: None)

    Returns:
        The result of reducing the collection
    """
    # Check if func is async
    if inspect.iscoroutinefunction(func):
        # Return an async generator
        async def async_reduce():
            if not collection:
                return initial

            # Get the first element if no initial value
            if initial is None:
                result = collection[0]
                items = collection[1:]
            else:
                result = initial
                items = collection

            # Apply func to each element
            for item in items:
                result = await func(result, item)

            return result

        # If we're in an async context, return the coroutine
        if is_async_context():
            return async_reduce()

        # Otherwise, run the coroutine in an event loop
        loop = get_or_create_event_loop()
        return loop.run_until_complete(async_reduce())

    # Regular reduce
    if not collection:
        return initial

    # Get the first element if no initial value
    if initial is None:
        result = collection[0]
        items = collection[1:]
    else:
        result = initial
        items = collection

    # Apply func to each element
    for item in items:
        result = func(result, item)

    return result


def is_async_context():
    """Check if the current context is asynchronous."""
    try:
        return inspect.currentframe().f_back.f_locals.get('__awaitable__', False)
    except (AttributeError, ValueError):
        return False


def get_or_create_event_loop():
    """Get the current event loop or create a new one if necessary."""
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        # No event loop in current thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


# Export utility functions for Runa runtime
__all__ = [
    'pipeline', 'partial', 'compose',
    'map_function', 'filter_function', 'reduce_function'
]