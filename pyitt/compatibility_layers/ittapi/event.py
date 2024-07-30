from pyitt import Event as _Event
from pyitt._named_region import _CallSite


class Event(_Event):
    """
    A class that represents Event.
    """
    def __str__(self) -> str:
        return self.name()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name()}')"

    def name(self):
        """Gets the name of the event."""
        return super().name


def event(region=None) -> Event:
    """
    Creates an Event instance.
    :param region: a name of the event or a callable object (e.g. function) to wrap. If the callable object is
                   passed the name of this object is used as a name for the event.
    :return: an Event instance
    """
    region = _CallSite(_CallSite.CallerFrame) if region is None else region
    return Event(region)
