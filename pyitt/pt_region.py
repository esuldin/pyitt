"""
pt_region.py - Python module wrapper for ITT PT API
"""
from functools import partial as _partial

from pyitt.native import PTRegion as _PTRegion

from ._named_region import _CallSite, _NamedRegion


class PTRegion(_NamedRegion):
    """
    A class that represents PT region.

    It provides control over collection of Intel Processor Trace (Intel PT) data.
    """
    def __init__(self, region=None):
        """
        Creates the instance of the class that represents ITT PT region.
        :param region: a name of the region or a callable object (e.g. function) to wrap. If the callable object is
                       passed the name of this object is used as a name for the region.
        """
        super().__init__(region)

        self.__pt_region = None
        self._on_name_determination = _partial(PTRegion.__deferred_pt_region_creation, self)

    def __deferred_pt_region_creation(self, name) -> None:
        """Performs deferred creation of native PT region."""
        self.__pt_region = _PTRegion(name)

    def begin(self) -> None:
        """Marks the beginning of a PT region."""
        self.__pt_region.begin()

    def end(self) -> None:
        """Marks the end of a PT region."""
        self.__pt_region.end()


def pt_region(region=None) -> PTRegion:
    """
    Creates a PT region instance.
    :param region: a name of the region or a callable object (e.g. function) to wrap. If the callable object is
                   passed the name of this object is used as a name for the region.
    :return: a PT region instance
    """
    region = _CallSite(_CallSite.CallerFrame) if region is None else region
    return PTRegion(region)
