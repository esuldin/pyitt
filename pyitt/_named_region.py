"""
_named_region.py - Python module wrapper for named code region
"""
from functools import partial as _partial
from inspect import stack as _stack
from os.path import basename as _basename

from ._region import _Region
from .string_handle import string_handle as _string_handle


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

        self.__name = self.__to_string_handle(self.__get_name(func))
        self.__name_determination_callback = None
        self.__is_final_name_determined = False

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

    def __set_name__(self, owner, name):
        self.__set_final_name(f'{self.__get_name(owner)}.{name}')

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

    def __set_final_name(self, name):
        """Sets a final name of a code region if it has not been done before."""
        if not self.__is_final_name_determined:
            self.__restore_original_begin_function()
            self.__name = self.__to_string_handle(name)
            self.__mark_name_as_final()

    def __wrap_callback(self, func):
        """Determines a final name of a code region if it has not been done before."""
        self.__set_final_name(self.__get_name(func))

    @staticmethod
    def __get_function(func):
        """Returns the argument if it is wrappable, otherwise returns None."""
        return func if _Region._is_wrappable(func) else None

    @staticmethod
    def __get_name(func):
        """Returns appropriate code region name."""
        if func is None:
            return None

        if isinstance(func, str):
            return func

        if isinstance(func, _CallSite):
            return f'{func.filename}:{func.lineno}'

        if hasattr(func, '__qualname__'):
            return func.__qualname__

        if hasattr(func, '__name__'):
            return func.__name__

        if hasattr(func, '__class__'):
            # PEP 3155 (Python 3.3) introduces __qualname__ on class objects
            return f'{func.__class__.__qualname__}.__call__'

        raise ValueError('Cannot get the name for the code region.')

    @staticmethod
    def __to_string_handle(s):
        """Creates StringHandle object from the passed object if it is not None, otherwise returns None."""
        return None if s is None else _string_handle(s)
