"""
frame.py - Python module wrapper for ITT Frame API
"""
from pyitt.native import frame_begin as _frame_begin, frame_end as _frame_end

from .domain import domain as _domain
from ._region import _Region


class Frame(_Region):
    """
    A class that represents Frame.
    """
    def __init__(self, region=None, domain=None, id=None):
        """
        Creates the instance of the class that represents ITT Frame.
        :param region: a callable object (e.g. function) to wrap
        :param domain: a frame domain
        :param id: a frame id
        """
        super().__init__(region)

        self.__domain = self.__get_domain(domain)
        self.__id = id

    def __str__(self) -> str:
        return f"{{ domain: '{str(self.__domain)}', id: {str(self.__id)} }}"

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({repr(self.__domain)}, {repr(self.__id)})'

    def domain(self):
        """Gets the domain of the frame."""
        return self.__domain

    def id(self):
        """Gets the id of the frame."""
        return self.__id

    def begin(self) -> None:
        """Marks the beginning of a frame region."""
        _frame_begin(self.__domain, self.__id)

    def end(self) -> None:
        """Marks the end of a frame region."""
        _frame_end(self.__domain, self.__id)

    @staticmethod
    def __get_domain(original_domain):
        """Gets frame domain"""
        if original_domain is None or isinstance(original_domain, str):
            return _domain(original_domain)

        return original_domain


def frame(region=None, domain=None, id=None) -> Frame:
    """
    Creates a Frame instance.
    :param region: a callable object (e.g. function) to wrap
    :param domain: a frame domain
    :param id: a frame id
    :return: a Frame instance
    """
    return Frame(region, domain, id)
