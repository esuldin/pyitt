from unittest import main as unittest_main, TestCase
from unittest.mock import Mock

from ...pyitt_native_mock import patch as pyitt_native_patch
from pyitt.compatibility_layers.itt_python import task_begin, task_end  # pylint: disable=C0411


class TaskTests(TestCase):
    @pyitt_native_patch('StringHandle')
    @pyitt_native_patch('task_begin')
    def test_task_begin_call(self, string_handle_class_mock, task_begin_mock):
        task_name = 'my task'

        domain_obj_mock = Mock()

        string_handle_obj_mock = Mock()
        string_handle_class_mock.return_value = string_handle_obj_mock

        task_begin(domain_obj_mock, task_name)

        domain_obj_mock.assert_not_called()
        string_handle_class_mock.assert_called_once_with(task_name)
        string_handle_obj_mock.assert_not_called()

        task_begin_mock.assert_called_once_with(domain_obj_mock, string_handle_obj_mock)

    @pyitt_native_patch('task_end')
    def test_task_end_call(self,  task_end_mock):
        domain_obj_mock = Mock()

        task_end(domain_obj_mock)

        domain_obj_mock.assert_not_called()
        task_end_mock.assert_called_once_with(domain_obj_mock)


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
