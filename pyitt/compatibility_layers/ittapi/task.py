from pyitt import task_begin as _task_begin, task_end as _task_end
from pyitt import task_begin_overlapped as _task_begin_overlapped, task_end_overlapped as _task_end_overlapped

from pyitt.task import _Task
from pyitt._named_region import _CallSite


class _CompatibleTask(_Task):
    """
    An abstract base class that provides common functionality for subtypes that represent ITT Tasks.
    """

    def __str__(self) -> str:
        return (f"{{ name: '{str(self.name())}', domain: '{str(self.domain())}',"
                f" id: {str(self.id())}, parent_id: {str(self.parent_id())} }}")

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}({repr(self.name())}, {repr(self.domain())},'
                f' {repr(self.id())}, {repr(self.parent_id())})')

    def domain(self):
        """Gets the domain of the task."""
        return super().domain

    def name(self):
        """Gets the name of the task."""
        return super().name

    def id(self):
        """Gets the id of the task."""
        return super().id

    def parent_id(self):
        """Gets the parent id for the task."""
        return super().parent_id


class NestedTask(_CompatibleTask):
    """
    A class that represents nested tasks.

    Nested tasks implicitly support a concept of embedded execution. This means that the call end() finalizes the
    most recent begin() call of the same or another nested task.
    """
    def begin(self) -> None:
        """Marks the beginning of a task."""
        _task_begin(self.domain(), self.name(), self.id(), self.parent_id())

    def end(self) -> None:
        """Marks the end of a task."""
        _task_end(self.domain())


def nested_task(task=None, domain=None, id=None, parent=None):
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


class OverlappedTask(_CompatibleTask):
    """
    A class that represents overlapped tasks.

    Execution regions of overlapped tasks may intersect.
    """
    def begin(self) -> None:
        """Marks the beginning of a task."""
        _task_begin_overlapped(self.domain(), self.name(), self.id(), self.parent_id())

    def end(self) -> None:
        """Marks the end of a task."""
        _task_end_overlapped(self.domain(), self.id())


def overlapped_task(task=None, domain=None, id=None, parent=None):
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


def task(task=None, domain=None, id=None, parent=None, overlapped=False):
    """
    Creates a task instance with the given arguments.
    :param task: a name of the task or a callable object
    :param domain: a task domain
    :param id: a task id
    :param parent: a parent task or an id of the parent
    :param overlapped: determines if the created task should be an instance of OverlappedTask class
                       or NestedTask class
    :return: a task instance
    """
    task = _CallSite(_CallSite.CallerFrame) if task is None else task
    return OverlappedTask(task, domain, id, parent) if overlapped else NestedTask(task, domain, id, parent)
