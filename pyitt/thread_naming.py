"""
thread_naming.py - Python module wrapper for ITT Thread Naming API
"""
from pyitt.native import thread_set_name as _thread_set_name


def thread_set_name(name: str):
    _thread_set_name(name)