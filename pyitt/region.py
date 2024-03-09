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
    """
    def __init__(self, func=None, wrap_callback=None) -> None:
        """
        Creates the instance of class that represents a traced code region.
        :param func: a callable object to wrap. If it is None, a wrapper creation will be deferred and can be done
                     using __call__() function for the object.
        :param wrap_callback: a callable object that will be called when wrapper is created.
        """
        self.__function = func
        self.__wrap_callback_function = wrap_callback

        if self.__function is None:
            self.__call_target = self.__wrap
        elif callable(self.__function):
            self.__call_wrap_callback()
            self.__call_target = self.__get_wrapper(self.__function)
            _wraps(self.__function, updated=())(self)
        else:
            raise TypeError('func must be a callable object or None.')

    def __get__(self, obj, objtype):
        return _wraps(self)(self.__get_wrapper(self.__function, obj))

    def __enter__(self) -> None:
        self.begin()

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
        """
        Call a callback for wrapper creation.
        """
        if callable(self.__wrap_callback_function):
            self.__wrap_callback_function(self.__function)

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
            A wrapper to trace the execution of a callable object
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
            A wrapper to trace the execution of a class method
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
        :param frame_number: relative frame number that should be used to extract the information about the call site
        """
        caller = _stack()[frame_number+1]
        self._filename = _basename(caller.filename)
        self._lineno = caller.lineno

    def filename(self):
        """Returns filename for the call site."""
        return self._filename

    def lineno(self):
        """Returns line number for the call site."""
        return self._lineno


class _NamedRegion(_Region):
    """
    An abstract base class that represents a named code region.
    """
    def __init__(self, code_region=None, name_creation_callback=None) -> None:
        """
        Creates the instance of class that represents a named code region.
        :param code_region: a name of the code region or a callable object (e.g. function) to wrap. If the callable
                            object is passed the name of this object is used as a name for the code region.
        """
        self._name = self.__get_code_region_name(code_region)
        self.__name_creation_callback = name_creation_callback
        self.__is_final_name_specified = not (code_region is None or isinstance(code_region, _CallSite))

        super().__init__(self.__get_function(code_region), _partial(_NamedRegion.__wrap_callback, self))

        if self.__is_final_name_specified:
            self.__call_name_creation_callback()

    def begin(self) -> None:
        """Marks the beginning of a code region."""
        raise NotImplementedError()

    def end(self) -> None:
        """Marks the end of a code region."""
        raise NotImplementedError()

    def name(self):
        """Return the name of the code region."""
        return self._name

    def __call_name_creation_callback(self):
        if callable(self.__name_creation_callback):
            self.__name_creation_callback(self._name)

    def __wrap_callback(self, func):
        if not self.__is_final_name_specified:
            self._name = self.__get_code_region_name(func)
            self.__call_name_creation_callback()
            self.__is_final_name_specified = True

    @staticmethod
    def __get_function(func):
        """Returns the argument if it is callable, otherwise returns None"""
        return func if callable(func) else None

    @staticmethod
    def __get_code_region_name(code_region):
        """Returns appropriate code region name"""
        if code_region is None:
            return None

        if isinstance(code_region, str):
            return _string_handle(code_region)

        if isinstance(code_region, _CallSite):
            return _string_handle(f'{code_region.filename()}:{code_region.lineno()}')

        if hasattr(code_region, '__qualname__'):
            return _string_handle(code_region.__qualname__)

        if hasattr(code_region, '__name__'):
            return _string_handle(code_region.__name__)

        if hasattr(code_region, '__class__'):
            return _string_handle(f'{code_region.__class__.__name__}.__call__')

        raise ValueError('Cannot get the name for the code region.')
