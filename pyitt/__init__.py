"""
Python binding to Intel Instrumentation and Tracing Technology (ITT) API.

This module provides a convenient way to mark up the Python code for further performance analysis using performance
analyzers from Intel like Intel VTune or others.
"""
from pyitt.native import Counter
from pyitt.native import Domain, Id, StringHandle
from pyitt.native import frame_begin, frame_end
from pyitt.native import task_begin, task_end, task_begin_overlapped, task_end_overlapped
from .collection_control import detach, pause, resume, active_region, paused_region, ActiveRegion, PausedRegion
from .counter import counter
from .domain import domain
from .event import event, Event
from .frame import frame, Frame
from .id import id
from .string_handle import string_handle
from .task import NestedTask, OverlappedTask, task, nested_task, overlapped_task
from .pt_region import PTRegion, pt_region
from .thread_naming import thread_set_name
