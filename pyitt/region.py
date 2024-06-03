"""
region.py - Python module wrapper for code region
"""
from functools import partial as _partial, wraps as _wraps
from inspect import stack as _stack
from os.path import basename as _basename

from .string_handle import string_handle as _string_handle


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
        self.__function = func
        self.__wrap_callback = None

        if self.__function is None:
            self.__call_target = self.__wrap
        elif callable(self.__function):
            self.__call_target = self.__get_wrapper(self.__function)
            _wraps(self.__function, updated=())(self)
        else:
            raise TypeError('func must be a callable object or None.')

    def __get__(self, obj, objtype):
        return _wraps(self)(self.__get_wrapper(self.__function, obj))

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

    @property
    def _on_wrapping(self):
        """Gets a callable object that will be called when wrapper is created if func is None."""
        return self.__wrap_callback

    @_on_wrapping.setter
    def _on_wrapping(self, callback):
        """Sets a callable object that will be called when wrapper is created if func is None."""
        self.__wrap_callback = callback

        if callable(self.__function):
            self.__call_wrap_callback()

    def __wrap(self, func):
        """
        Wraps a callable object.
        :param func: a callable object to wrap
        :return: a wrapper to trace the execution of the callable object
        """
        if callable(func):
            self.__function = func
        else:
            raise TypeError('Callable object is expected as a first argument.')

        self.__call_wrap_callback()

        return _wraps(self.__function)(self.__get_wrapper(self.__function))

    def __call_wrap_callback(self):
        """Call a callback for wrapper creation."""
        if callable(self.__wrap_callback):
            self.__wrap_callback(self.__function)

    def __get_wrapper(self, func, obj=None):
        """
        Returns a pure wrapper for a callable object.
        :param func: the callable object to wrap
        :param obj: an object to which the callable object is bound
        :return: the wrapper to trace the execution of the callable object
        """
        if not callable(func):
            raise TypeError('Callable object is expected to be passed.')

        def _function_wrapper(*args, **kwargs):
            """
            A wrapper to trace the execution of a callable object.
            :param args: positional arguments of the callable object
            :param kwargs: keyword arguments of the callable object
            :return: result of a call of the callable object
            """
            self.begin()

            try:
                func_result = func(*args, **kwargs)
            finally:
                self.end()

            return func_result

        def _method_wrapper(*args, **kwargs):
            """
            A wrapper to trace the execution of a class method.
            :param args: positional arguments of the class method
            :param kwargs: keyword arguments of the class method
            :return: result of a call of the class method
            """
            self.begin()

            try:
                func_result = func(obj, *args, **kwargs)
            finally:
                self.end()

            return func_result

        return _function_wrapper if obj is None or isinstance(func, staticmethod) else _method_wrapper


class _CallSite:
    """
    A class that represents a call site for a callable object.
    """
    CallerFrame = 1

    def __init__(self, frame_number: int) -> None:
        """
        Creates a call site.
        :param frame_number: relative frame number that should be used to extract the information about the call site.
        """
        caller = _stack()[frame_number+1]
        self._filename = _basename(caller.filename)
        self._lineno = caller.lineno

    @property
    def filename(self) -> str:
        """Returns filename for the call site."""
        return self._filename

    @property
    def lineno(self) -> int:
        """Returns line number for the call site."""
        return self._lineno


class _NamedRegion(_Region):
    """
    An abstract base class that represents a named code region.
    """
    def __init__(self, func=None) -> None:
        """
        Creates the instance of class that represents a named code region.
        :param func: a name of the code region, a call site for the code region or a callable object (e.g. function) to
                     wrap.
                     If the call site object is passed, it is used as the initial choice for the region name. The name
                     that was derived based on call site object can be replaced with the name of the callable object if
                     it is passed in the future.
                     If the callable object is passed the name of this object is used as a name for the code region.
        """
        super().__init__(self.__get_function(func))

        self.__name = self.__get_name(func)
        self.__name_determination_callback = None
        self.__is_final_name_determined = False
        self.__is_custom_name_specified = isinstance(func, str)

        final_name_is_determined = not (func is None or isinstance(func, _CallSite))
        if final_name_is_determined:
            self.__original_begin_func = None
            self.__mark_name_as_final()
        else:
            self._on_wrapping = _partial(_NamedRegion.__wrap_callback, self)

            self.__original_begin_func = self.begin
            self.begin = self.__begin_wrapper

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"

    def begin(self) -> None:
        """Marks the beginning of a code region."""
        raise NotImplementedError()

    def end(self) -> None:
        """Marks the end of a code region."""
        raise NotImplementedError()

    @property
    def name(self):
        """Returns the name of the code region."""
        return self.__name

    @property
    def _on_name_determination(self):
        """Gets a callable object that will be called when final name of a region is determined."""
        return self.__name_determination_callback

    @_on_name_determination.setter
    def _on_name_determination(self, callback):
        """Sets a callable object that will be called when final name of a region is determined."""
        self.__name_determination_callback = callback

        if self.__is_final_name_determined:
            self.__call_name_determination_callback()

    def __begin_wrapper(self):
        """A wrapper for _Region.begin() function that is used to mark the current name of a region as final."""
        self.__restore_original_begin_function()
        self.__mark_name_as_final()
        self.begin()

    def __call_name_determination_callback(self):
        """Calls a name determination callback."""
        if callable(self.__name_determination_callback):
            self.__name_determination_callback(self.name)

    def __mark_name_as_final(self):
        """Marks the current name as a final name of a code region."""
        self.__is_final_name_determined = True
        self.__call_name_determination_callback()

    def __restore_original_begin_function(self):
        """Removes the wrapper for _Region.begin() function."""
        if self.__original_begin_func is not None:
            self.begin = self.__original_begin_func
            self.__original_begin_func = None

    def __wrap_callback(self, func):
        """Determines a final name of a code region if it has not been done before."""
        if not self.__is_final_name_determined:
            self.__restore_original_begin_function()
            self.__name = self.__get_name(func)
            self.__mark_name_as_final()
        elif not self.__is_custom_name_specified:
            raise RuntimeError(f'A custom name for a code region must be specified before'
                               f' {self.__class__.__name__}.__call__() can be called more than once.')

    @staticmethod
    def __get_function(func):
        """Returns the argument if it is callable, otherwise returns None."""
        return func if callable(func) else None

    @staticmethod
    def __get_name(func):
        """Returns appropriate code region name."""
        if func is None:
            return None

        if isinstance(func, str):
            return _string_handle(func)

        if isinstance(func, _CallSite):
            return _string_handle(f'{func.filename}:{func.lineno}')

        if hasattr(func, '__qualname__'):
            return _string_handle(func.__qualname__)

        if hasattr(func, '__name__'):
            return _string_handle(func.__name__)

        if hasattr(func, '__class__'):
            return _string_handle(f'{func.__class__.__name__}.__call__')

        raise ValueError('Cannot get the name for the code region.')
