"""
test_task.py - Python module wrapper for ITT Task API
"""
from functools import partial as _partial, wraps as _wraps
from inspect import stack as _stack
from os.path import basename as _basename

from pyitt.native import task_begin as _task_begin, task_end as _task_end
from pyitt.native import task_begin_overlapped as _task_begin_overlapped, task_end_overlapped as _task_end_overlapped

from .domain import domain as _domain
from .id import id as _id
from .string_handle import string_handle as _string_handle


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


class _Task:
    """
    An abstract base class that provides common functionality for subtypes that represent ITT Tasks.

    The subclasses itself and instances of the subclasses can be used as a context manager or as a decorator
    to automatically track the execution of code sections and callable objects (e.g. function).
    """
    def __init__(self, task=None, domain=None, id=None, parent=None) -> None:
        """
        Creates the instance of class that represents ITT task.
        :param task: a name of the task or a callable object (e.g. function) to wrap. If the callable object is passed
                     the name of this object is used as a name for the task.
        :param domain: a task domain
        :param id: a task id
        :param parent: a parent task or an id of the parent
        """
        self._function = self._get_function(task)
        if self._function is None:
            self._call_target = self._wrap
        else:
            self._call_target = self._wrapper

        self._name, self._is_call_site_used_as_name = self._get_task_name(task)
        self._domain = self._get_task_domain(domain)
        self._id = self._get_task_id(id, self._domain)
        self._parent_id = self._get_parent_id(parent)

    def __enter__(self) -> None:
        self.begin()

    def __exit__(self, *args) -> None:
        self.end()

    def __call__(self, *args, **kwargs):
        return self._call_target(*args, **kwargs)

    def __str__(self) -> str:
        return (f"{{ name: '{str(self._name)}', domain: '{str(self._domain)}',"
                f" id: {str(self._id)}, parent_id: {str(self._parent_id)}")

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}({repr(self._name)}, {repr(self._domain)},'
                f' {repr(self._id)}, {repr(self._parent_id)})')

    def name(self):
        """Return the name of the task."""
        return self._name.str

    def domain(self):
        """Returns the domain of the task."""
        return self._domain

    def id(self):
        """Returns the id of the task."""
        return self._id

    def parent_id(self):
        """Returns the parent id for the task."""
        return self._parent_id

    def begin(self) -> None:
        """Marks the beginning of a task."""
        raise NotImplementedError()

    def end(self) -> None:
        """Marks the end of a task."""
        raise NotImplementedError()

    def _wrap(self, func):
        """
        Wraps a callable object.
        :param func: a callable object to wrap
        :return: a wrapper to trace the execution of the callable object
        """
        self._function = self._get_function(func)
        if self._function is None:
            raise TypeError('Callable object is expected as a first argument.')

        if self._is_call_site_used_as_name:
            self._name, self._is_call_site_used_as_name = self._get_task_name(self._function)

        return _wraps(self._function)(_partial(NestedTask._wrapper, self))

    def _wrapper(self, *args, **kwargs):
        """
        A wrapper to trace the execution of a callable object
        :param args: positional arguments of the callable object
        :param kwargs: keyword arguments of the callable object
        :return: result of a call of the callable object
        """
        self.begin()
        func_result = self._function(*args, **kwargs)
        self.end()
        return func_result

    @staticmethod
    def _get_function(func):
        """Returns the argument if it is callable, otherwise returns None"""
        return func if callable(func) else None

    @staticmethod
    def _get_task_name(original_task):
        """Returns appropriate task name"""
        is_call_site_name_used = False
        name = None
        if original_task is None:
            pass
        elif isinstance(original_task, str):
            name = _string_handle(original_task)
        elif isinstance(original_task, _CallSite):
            name = _string_handle(f'{original_task.filename()}:{original_task.lineno()}')
            is_call_site_name_used = True
        else:
            name = _string_handle(original_task.__qualname__)

        return name, is_call_site_name_used

    @staticmethod
    def _get_task_domain(original_domain):
        """Returns task domain"""
        if original_domain is None or isinstance(original_domain, str):
            return _domain(original_domain)
        else:
            return original_domain

    @staticmethod
    def _get_task_id(original_id, domain):
        """Returns task id for specified domain"""
        return _id(domain) if original_id is None else original_id

    @staticmethod
    def _get_parent_id(original_parent):
        """Returns parent id"""
        return original_parent.id() if isinstance(original_parent, task.__class__) else original_parent


class NestedTask(_Task):
    """
    A class that represents nested tasks.

    Nested tasks implicitly support a concept of embedded execution. This means that the call end() finalizes the
    most recent begin() call of the same or another nested task.
    """
    def begin(self) -> None:
        """Marks the beginning of a task."""
        _task_begin(self._domain, self._name, self._id, self._parent_id)

    def end(self) -> None:
        """Marks the end of a task."""
        _task_end(self._domain)


def nested_task(task=None, domain=None, id=None, parent=None):
    """

    :param task: a name of the task or a callable object
    :param domain: a task domain
    :param id: a task id
    :param parent: a parent task or an id of the parent
    :return:
    """
    task = _CallSite(_CallSite.CallerFrame) if task is None else task
    return NestedTask(task, domain, id, parent)


class OverlappedTask(_Task):
    """
    A class that represents overlapped tasks.

    Execution regions of overlapped tasks may intersect.
    """
    def begin(self) -> None:
        """Marks the beginning of a task."""
        _task_begin_overlapped(self._domain, self._name, self._id, self._parent_id)

    def end(self) -> None:
        """Marks the end of a task."""
        _task_end_overlapped(self._domain, self._id)


def overlapped_task(task=None, domain=None, id=None, parent=None):
    """
    Creates an OverlapedTask instance with the given arguments.
    :param task: a name of the task or a callable object
    :param domain: a task domain
    :param id: a task id
    :param parent: a parent task or an id of the parent
    :return:
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
    :return: task instance
    """
    task = _CallSite(_CallSite.CallerFrame) if task is None else task
    return OverlappedTask(task, domain, id, parent) if overlapped else NestedTask(task, domain, id, parent)
