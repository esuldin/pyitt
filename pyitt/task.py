"""
task.py - Python module wrapper for ITT Task API
"""
from pyitt.native import task_begin as _task_begin, task_end as _task_end
from pyitt.native import task_begin_overlapped as _task_begin_overlapped, task_end_overlapped as _task_end_overlapped

from ._funcutils import is_coroutine_function as _is_coroutine_function
from .domain import domain as _domain
from .id import id as _id
from ._named_region import _CallSite, _NamedRegion


class _Task(_NamedRegion):
    """
    An abstract base class that provides common functionality for subtypes that represent ITT Tasks.
    """
    def __init__(self, task=None, /, domain=None, id=None, parent=None) -> None:
        """
        Creates the instance of the class that represents an ITT task.
        :param task: a name of the task or a callable object (e.g. function) to wrap. If the callable object is passed
                     the name of this object is used as a name for the task.
        :param domain: a task domain
        :param id: a task id
        :param parent: a parent task or an id of the parent
        """
        super().__init__(task)

        self.__domain = self.__get_task_domain(domain)
        self.__id = self.__get_task_id(id, self.__domain)
        self.__parent_id = self.__get_parent_id(parent)

    def __str__(self) -> str:
        return (f"{{ name: '{str(self.name)}', domain: '{str(self.domain)}',"
                f" id: {str(self.id)}, parent_id: {str(self.parent_id)} }}")

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}({repr(self.name)}, {repr(self.domain)},'
                f' {repr(self.id)}, {repr(self.parent_id)})')

    @property
    def domain(self):
        """Returns the domain of the task."""
        return self.__domain

    @property
    def id(self):
        """Returns the id of the task."""
        return self.__id

    @property
    def parent_id(self):
        """Returns the parent id for the task."""
        return self.__parent_id

    def begin(self) -> None:
        """Marks the beginning of the task."""
        raise NotImplementedError()

    def end(self) -> None:
        """Marks the end of the task."""
        raise NotImplementedError()

    @staticmethod
    def __get_task_domain(original_domain):
        """Returns the domain of the task."""
        if original_domain is None or isinstance(original_domain, str):
            return _domain(original_domain)

        return original_domain

    @staticmethod
    def __get_task_id(original_id, domain):
        """Returns task id for the specified domain."""
        return _id(domain) if original_id is None else original_id

    @staticmethod
    def __get_parent_id(original_parent):
        """Returns parent id."""
        return original_parent.id() if isinstance(original_parent, task.__class__) else original_parent


class NestedTask(_Task):
    """
    A class that represents nested tasks.

    Nested tasks implicitly support a concept of embedded execution. This means that the call end() finalizes the
    most recent begin() call of the same or another nested task.
    """
    def begin(self) -> None:
        """Marks the beginning of the task."""
        _task_begin(self.domain, self.name, self.id, self.parent_id)

    def end(self) -> None:
        """Marks the end of the task."""
        _task_end(self.domain)


def nested_task(task=None, /, domain=None, id=None, parent=None):
    """
    Creates a nested task instance with the given arguments.
    :param task: a name of the task or a callable object
    :param domain: a task domain
    :param id: a task id
    :param parent: a parent task or an id of the parent
    :return: an instance of NestedTask
    """
    task = _CallSite(_CallSite.CallerFrame) if task is None else task
    return NestedTask(task, domain, id, parent)


class OverlappedTask(_Task):
    """
    A class that represents overlapped tasks.

    Execution regions of overlapped tasks may intersect.
    """
    def begin(self) -> None:
        """Marks the beginning of the task."""
        _task_begin_overlapped(self.domain, self.name, self.id, self.parent_id)

    def end(self) -> None:
        """Marks the end of the task."""
        _task_end_overlapped(self.domain, self.id)


def overlapped_task(task=None, /, domain=None, id=None, parent=None):
    """
    Creates an overlapped task instance with the given arguments.
    :param task: a name of the task or a callable object
    :param domain: a task domain
    :param id: a task id
    :param parent: a parent task or an id of the parent
    :return: an instance of OverlappedTask
    """
    task = _CallSite(_CallSite.CallerFrame) if task is None else task
    return OverlappedTask(task, domain, id, parent)


def task(task=None, /, domain=None, id=None, parent=None):
    """
    Creates a task instance with the given arguments.
    :param task: a name of the task or a callable object
    :param domain: a task domain
    :param id: a task id
    :param parent: a parent task or an id of the parent
    :return: an OverlappedTask task instance if task is a coroutine function, otherwise, a NestedTask instance
    """
    can_be_overlapped = _is_coroutine_function(task)
    task = _CallSite(_CallSite.CallerFrame) if task is None else task
    return OverlappedTask(task, domain, id, parent) if can_be_overlapped else NestedTask(task, domain, id, parent)
