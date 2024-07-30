"""
Compatibility layer for itt-python.

This module provides a compatibility layer that allows to use pyitt as a backend for itt-python
(https://github.com/NERSC/itt-python).
"""
from pyitt.native import detach, pause, resume

from .domain import domain_create
from .pt_region import pt_region_create, pt_region_begin, pt_region_end
from .task import task_begin, task_end
