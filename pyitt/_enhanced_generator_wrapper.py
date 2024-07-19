"""
_enhanced_generator_wrapper.py - Python module with wrappers for enhanced generator objects
"""
from collections.abc import Coroutine as _Coroutine, Generator as _Generator


class _GeneratorObjectWrapper(_Generator):
    """
    A class that provides the functionality to trace a generator.
    """
    def __init__(self, obj, begin_func, end_func):
        """
        Creates the instance of class to trace a generator object.
        :param obj: the generator object to trace
        :param begin_func: a function that will be called to mark the beginning of generator execution
        :param end_func: a function that will be called to mark the end of generator execution
        """
        self.__object = obj
        self.__begin_func = begin_func
        self.__end_func = end_func
        self.__is_started = False

    def __iter__(self):
        return self

    def __next__(self):
        return self.send(None)

    def send(self, value):
        """Resumes the generator and "sends" a value that becomes the result of the current yield-expression."""
        try:
            self.__begin()
            return self.__object.send(value)
        except:  # noqa: E722
            self.__end()
            raise

    def throw(self, *args, **kwargs):
        """Raises an exception inside the generator."""
        try:
            self.__begin()
            return self.__object.throw(*args, **kwargs)
        except:  # noqa: E722
            self.__end()
            raise

    def close(self):
        """Terminates the iteration."""
        try:
            return self.__object.close()
        finally:
            self.__end()

    def __begin(self):
        """Marks the beginning of the generator execution."""
        if not self.__is_started:
            self.__begin_func()
            self.__is_started = True

    def __end(self):
        """Marks the end of the generator execution."""
        if self.__is_started:
            self.__end_func()


class _AwaitableObjectWrapper(_Coroutine):
    """
    A class that provides the functionality to trace a coroutine.
    """
    def __init__(self, obj, begin_func, end_func):
        self.__object = obj
        self.__begin_func = begin_func
        self.__end_func = end_func
        self.__is_started = False

    def __await__(self):
        return self

    def __next__(self):
        return self.send(None)

    def send(self, value):
        """Resumes the coroutine and "sends" a value that becomes the result of the current yield-expression."""
        try:
            self.__begin()
            return self.__object.send(value)
        except:  # noqa: E722
            self.__end()
            raise

    def throw(self, *args, **kwargs):
        """Raises an exception inside the generator."""
        try:
            self.__begin()
            return self.__object.throw(*args, **kwargs)
        except:  # noqa: E722
            self.__end()
            raise

    def close(self):
        """Terminates the coroutine."""
        try:
            return self.__object.close()
        finally:
            self.__end()

    def __begin(self):
        """Marks the beginning of the coroutine execution."""
        if not self.__is_started:
            self.__begin_func()
            self.__is_started = True

    def __end(self):
        """Marks the end of the coroutine execution."""
        if self.__is_started:
            self.__end_func()
