from pyitt import PTRegion as _PTRegion
from pyitt._named_region import _CallSite


class PTRegion(_PTRegion):
    """
    A class that represents PT region.

    It provides control over collection of Intel Processor Trace (Intel PT) data.
    """
    def __str__(self) -> str:
        return self.name()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name()}')"

    def name(self):
        """Gets the name of the PT region."""
        return super().name

    def get_pt_region(self):
        """Gets the PT region."""
        return self


def pt_region(region=None) -> PTRegion:
    """
    Creates a PT region instance.
    :param region: a name of the region or a callable object (e.g. function) to wrap. If the callable object is
                   passed the name of this object is used as a name for the region.
    :return: a PT region instance
    """
    region = _CallSite(_CallSite.CallerFrame) if region is None else region
    return PTRegion(region)
