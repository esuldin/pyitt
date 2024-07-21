"""
counter.py - Python module wrapper for ITT Counter API
"""
from pyitt.native import Counter as _Counter


def counter(name, domain=None, init_value=None):
    """
    Creates a counter with the given name, domain and initial value.
    :param name: a name of the counter
    :param domain: a name of the domain
    :param init_value: an initial value of the counter
    :return: an instance of Counter
    """
    return _Counter(name, domain, init_value)
