"""
region.py - Python module wrapper for code region
"""
from functools import partial as _partial, wraps as _wraps


class _Region:
    """
    An abstract base class that provides common functionality to wrap a code region.

    The subclasses itself and instances of the subclasses can be used as a context manager or as a decorator
    to automatically track the execution of code region and callable objects (e.g. function).
    """
    def __init__(self, func=None, wrap_callback=None) -> None:
        """
        Creates the instance of class that represents ITT task.
        :param func: a callable object to wrap. If it is None, a wrapper creation will be deferred and can be done
                     using __call__() function for the object.
        :param wrap_callback: a callable object that will be called for deferred wrapper creation.
        """
        self._function = func
        if self._function is None:
            self._call_target = self._wrap
        elif callable(func):
            self._call_target = self._wrapper
            _wraps(func, updated=())(self)
        else:
            raise TypeError('func must be a callable object.')
        self._wrap_callback_function = wrap_callback

    def __enter__(self) -> None:
        self.begin()

    def __exit__(self, *args) -> None:
        self.end()

    def __call__(self, *args, **kwargs):
        return self._call_target(*args, **kwargs)

    def begin(self) -> None:
        """Marks the beginning of a code region."""
        raise NotImplementedError()

    def end(self) -> None:
        """Marks the end of a code region."""
        raise NotImplementedError()

    def _wrap(self, func):
        """
        Wraps a callable object.
        :param func: a callable object to wrap
        :return: a wrapper to trace the execution of the callable object
        """
        if callable(func):
            self._function = func
        else:
            raise TypeError('Callable object is expected as a first argument.')

        if callable(self._wrap_callback_function):
            self._wrap_callback_function(func)

        return _wraps(self._function)(_partial(_Region._wrapper, self))

    def _wrapper(self, *args, **kwargs):
        """
        A wrapper to trace the execution of a callable object
        :param args: positional arguments of the callable object
        :param kwargs: keyword arguments of the callable object
        :return: result of a call of the callable object
        """
        self.begin()
        func_result = self._function(*args, **kwargs)
        self.end()
        return func_result
