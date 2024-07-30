"""
Compatibility layer for ittapi.

This module provides a compatibility layer that allows to use pyitt as a backend for ittapi Python bindings
(https://github.com/intel/ittapi/tree/master/python).
"""
from pyitt.native import Domain, Id, StringHandle
from pyitt.native import task_begin, task_end, task_begin_overlapped, task_end_overlapped
from pyitt.collection_control import detach, pause, resume, active_region, paused_region, ActiveRegion, PausedRegion
from pyitt.domain import domain
from pyitt.id import id
from pyitt.string_handle import string_handle
from pyitt.thread_naming import thread_set_name

from .event import event, Event
from .pt_region import pt_region
from .task import NestedTask, OverlappedTask, task, nested_task, overlapped_task
