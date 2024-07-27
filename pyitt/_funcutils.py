"""
_funcutils.py - Python module with internal tools for working with callable objects
"""
from asyncio import iscoroutinefunction as _asyncio_iscoroutinefunction
from inspect import iscoroutinefunction as _iscoroutinefunction
from sys import version_info


def is_coroutine_function(func):
    """Returns True if the object is a coroutine function. Otherwise, returns False."""
    return _iscoroutinefunction(func) or _asyncio_iscoroutinefunction(func)


def mark_coroutine_function(func):
    """Marks an object as a coroutine function."""
    # pylint: disable=C0415,W0212
    from asyncio.coroutines import _is_coroutine
    func._is_coroutine = _is_coroutine

    if version_info >= (3, 12):
        from inspect import markcoroutinefunction
        markcoroutinefunction(func)
