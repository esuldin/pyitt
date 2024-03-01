from types import ModuleType as _ModuleType
from unittest.mock import MagicMock as _MagicMock

PYITT_NATIVE_MODULE_NAME = 'pyitt.native'


class PyittNativeMock(_ModuleType):
    def __init__(self):
        super(PyittNativeMock, self).__init__(PYITT_NATIVE_MODULE_NAME)
        self.attrs = {
            'task_begin': _MagicMock(),
            'task_end': _MagicMock(),
            'Domain': _MagicMock(),
            'Id': _MagicMock(),
            'StringHandle': _MagicMock(),
        }

    def __getattr__(self, item):
        return self.attrs.get(item)

    def attributes(self):
        return self.attrs
