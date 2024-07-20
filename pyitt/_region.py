"""
_region.py - Python module wrapper for code region
"""
from collections.abc import Coroutine as _Coroutine, Generator as _Generator
from functools import lru_cache as _lru_cache, wraps as _wraps
from inspect import ismethoddescriptor as _ismethoddescriptor, isgeneratorfunction as _isgeneratorfunction

from ._funcutils import is_coroutine_function as _is_coroutine_function
from ._funcutils import mark_coroutine_function as _mark_coroutine_function


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


class _Region:
    """
    An abstract base class that provides common functionality to wrap a code region.

    The subclasses itself and instances of the subclasses can be used as a context manager or as a decorator
    to automatically track the execution of code region and callable objects (e.g. function).

    Although the class instance can be used to wrap any callable objects. It is not supposed that it will act as a proxy
    for instances of classes that implement the `__call__()` method. It means that the instance will not be a descendant
    of the passed object's class, and it will not provide the access to attributes of the passed object.
    """
    def __init__(self, func=None) -> None:
        """
        Creates the instance of class that represents a traced code region.
        :param func: a callable object to wrap. If it is None, a wrapper creation will be deferred and can be done
                     using `__call__()` method for the instance.
        """
        self.__function = None
        self.__wrap_callback = None

        self._is_coroutine = None
        self._is_coroutine_marker = None

        if func is None:
            self.__call_target = self.__wrap
        elif self._is_wrappable(func):
            self.__wrap(func)
        else:
            raise TypeError('func must be a callable object, method descriptor or None.')

    def __get__(self, obj, objtype=None):
        return self.__get_method_wrapper(self.__function, obj)

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, *args) -> None:
        self.end()

    def __call__(self, *args, **kwargs):
        return self.__call_target(*args, **kwargs)

    def begin(self) -> None:
        """Marks the beginning of a code region."""
        raise NotImplementedError()

    def end(self) -> None:
        """Marks the end of a code region."""
        raise NotImplementedError()

    @staticmethod
    def _is_wrappable(func):
        """Returns True if the func can be wrapped, otherwise False."""
        return callable(func) or _ismethoddescriptor(func)

    @property
    def _on_wrapping(self):
        """Gets a callable object that will be called when wrapper is created if func is None."""
        return self.__wrap_callback

    @_on_wrapping.setter
    def _on_wrapping(self, callback):
        """Sets a callable object that will be called when wrapper is created if func is None."""
        self.__wrap_callback = callback

        if self._is_wrappable(self.__function):
            self.__call_wrap_callback()

    def __wrap(self, func):
        """
        Wraps a callable object.
        :param func: a callable object to wrap
        :return: a wrapper to trace the execution of the callable object
        """
        if not self._is_wrappable(func):
            raise TypeError('Callable object or method descriptor are expected to be passed.')

        self.__function = func
        self.__call_wrap_callback()
        self.__call_target = self.__get_wrapper(self.__function)

        if _is_coroutine_function(self.__function):
            _mark_coroutine_function(self)
        _wraps(self.__function, updated=())(self)

        return self

    def __call_wrap_callback(self):
        """Call a callback for wrapper creation."""
        if callable(self.__wrap_callback):
            self.__wrap_callback(self.__function)

    def __get_wrapper_for_async_callable_object(self, func, obj=None):
        def _async_function_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return _AwaitableObjectWrapper(result, self.begin, self.end)

        def _async_method_wrapper(*args, **kwargs):
            result = func(obj, *args, **kwargs)
            return _AwaitableObjectWrapper(result, self.begin, self.end)

        return _async_function_wrapper if obj is None else _async_method_wrapper

    def __get_wrapper_for_generator_object(self, func, obj=None):
        def _generator_function_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return _GeneratorObjectWrapper(result, self.begin, self.end)

        def _generator_method_wrapper(*args, **kwargs):
            result = func(obj, *args, **kwargs)
            return _GeneratorObjectWrapper(result, self.begin, self.end)

        return _generator_function_wrapper if obj is None else _generator_method_wrapper

    def __get_wrapper_for_sync_callable_object(self, func, obj=None):
        begin_func = self.begin
        end_func = self.end

        if _ismethoddescriptor(func):
            obj_type = type(obj)
            descr_get = func.__get__

            def _descriptor_wrapper(*args, **kwargs):
                """
                A wrapper to trace the execution of a callable object that is returned by the method descriptor object.
                :param args: positional arguments of the callable object
                :param kwargs: keyword arguments of the callable object
                :return: result of a call of a returned function by the method descriptor object
                """
                target_func = descr_get(obj, obj_type)

                if _is_coroutine_function(target_func):
                    result = target_func(*args, **kwargs)
                    return _AwaitableObjectWrapper(result, begin_func, end_func)
                if _isgeneratorfunction(target_func):
                    result = target_func(*args, **kwargs)
                    return _GeneratorObjectWrapper(result, begin_func, end_func)

                begin_func()
                try:
                    return target_func(*args, **kwargs)
                finally:
                    end_func()

            return _descriptor_wrapper

        def _function_wrapper(*args, **kwargs):
            """
            A wrapper to trace the execution of a callable object.
            :param args: positional arguments of the callable object
            :param kwargs: keyword arguments of the callable object
            :return: result of a call of the callable object
            """
            begin_func()

            try:
                return func(*args, **kwargs)
            finally:
                end_func()

        def _method_wrapper(*args, **kwargs):
            """
            A wrapper to trace the execution of a class method.
            :param args: positional arguments of the class method
            :param kwargs: keyword arguments of the class method
            :return: result of a call of the class method
            """
            begin_func()

            try:
                return func(obj, *args, **kwargs)
            finally:
                end_func()

        return _function_wrapper if obj is None else _method_wrapper

    def __get_wrapper(self, func, obj=None):
        """
        Returns a pure wrapper for a callable object.
        :param func: the callable object to wrap
        :param obj: an object to which the callable object is bound
        :return: the wrapper to trace the execution of the callable object
        """
        if not self._is_wrappable(func):
            raise TypeError('Callable object or method descriptor are expected to be passed.')

        if _is_coroutine_function(func):
            return self.__get_wrapper_for_async_callable_object(func, obj)

        if _isgeneratorfunction(func):
            return self.__get_wrapper_for_generator_object(func, obj)

        return self.__get_wrapper_for_sync_callable_object(func, obj)

    @_lru_cache
    def __get_method_wrapper(self, func, obj):
        wrapper = self.__get_wrapper(func, obj)
        if _is_coroutine_function(func):
            _mark_coroutine_function(wrapper)
        return _wraps(func)(wrapper)
