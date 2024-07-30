from pyitt.native import StringHandle as _StringHandle
from pyitt.native import task_begin as _task_begin, task_end as _task_end


def task_begin(domain, name) -> None:
    """
    Marks the beginning of the task.
    :param domain: a task domain
    :param name: a name of the task
    :return: None
    """
    _task_begin(domain, _StringHandle(name))


def task_end(domain) -> None:
    """
    Marks the end of the task.
    :param domain: a task domain
    :return: None
    """
    _task_end(domain)
