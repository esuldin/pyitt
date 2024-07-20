from types import ModuleType as _ModuleType
from unittest.mock import Mock as _Mock

PYITT_NATIVE_MODULE_NAME = 'pyitt.native'


class PyittNativeMock(_ModuleType):
    def __init__(self):
        super().__init__(PYITT_NATIVE_MODULE_NAME)
        self.attrs = {
            'detach': _Mock(),
            'pause': _Mock(),
            'resume': _Mock(),
            'frame_begin': _Mock(),
            'frame_end': _Mock(),
            'task_begin': _Mock(),
            'task_end': _Mock(),
            'task_begin_overlapped': _Mock(),
            'task_end_overlapped': _Mock(),
            'thread_set_name': _Mock(),
            'Domain': _Mock(),
            'Event': _Mock(),
            'Id': _Mock(),
            'StringHandle': _Mock(),
        }

    def __getattr__(self, item):
        return self.attrs.get(item)

    def attributes(self):
        return self.attrs
