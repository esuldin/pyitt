"""
collection_control.py - Python module wrapper for ITT Collection Control API
"""
from pyitt.native import detach as _detach, pause as _pause, resume as _resume


def detach() -> None:
    """Detach collection of profiling data."""
    _detach()


def pause() -> None:
    """Pause collection of profiling data."""
    _pause()


def resume() -> None:
    """Resume collection of profiling data."""
    _resume()
