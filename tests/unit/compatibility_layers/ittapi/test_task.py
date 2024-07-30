from inspect import stack
from os.path import basename
from unittest import main as unittest_main, TestCase
from unittest.mock import call

from ...pyitt_native_mock import patch as pyitt_native_patch
import pyitt.compatibility_layers.ittapi as ittapi  # pylint: disable=C0411


class TaskCreationTests(TestCase):
    @pyitt_native_patch('Domain')
    @pyitt_native_patch('StringHandle')
    @pyitt_native_patch('Id')
    def test_task_creation_with_default_constructor(self, domain_class_mock, string_handle_class_mock, id_class_mock):
        domain_class_mock.return_value = 'pyitt'
        string_handle_class_mock.side_effect = lambda x: x
        id_class_mock.return_value = 1

        task = ittapi.task()
        caller = stack()[0]
        expected_name = f'{basename(caller.filename)}:{caller.lineno-1}'

        string_handle_class_mock.assert_called_once_with(expected_name)
        domain_class_mock.assert_called_once_with(None)

        self.assertIsInstance(task, ittapi.NestedTask)
        self.assertEqual(task.name(), expected_name)
        self.assertEqual(task.domain(), domain_class_mock.return_value)
        self.assertEqual(task.id(), id_class_mock.return_value)
        self.assertIsNone(task.parent_id())

    @pyitt_native_patch('StringHandle')
    def test_task_creation_as_decorator_for_function(self, string_handle_class_mock):
        @ittapi.task
        def my_function():
            pass  # pragma: no cover

        string_handle_class_mock.assert_called_once_with(my_function.__qualname__)

    @pyitt_native_patch('StringHandle')
    def test_task_creation_as_decorator_with_name_for_function(self, string_handle_class_mock):
        @ittapi.task('my function')
        def my_function():
            pass  # pragma: no cover

        string_handle_class_mock.assert_called_once_with('my function')

    def test_task_creation_overlapped_task(self):
        task = ittapi.task(overlapped=True)
        self.assertIsInstance(task, ittapi.OverlappedTask)


class TaskPropertiesTest(TestCase):
    @pyitt_native_patch('Domain')
    @pyitt_native_patch('Id')
    @pyitt_native_patch('StringHandle')
    def test_task_properties(self, domain_class_mock, id_class_mock, string_handle_class_mock):
        domain_class_mock.side_effect = lambda x: x
        string_handle_class_mock.side_effect = lambda x: x
        id_class_mock.return_value = lambda x: x

        class CallableClass:
            def __call__(self, *args, **kwargs):
                pass  # pragma: no cover

        domain_name = 'my domain'
        task_id = 2
        parent_id = 1
        task = ittapi.task(CallableClass(), domain=domain_name, id=task_id, parent=parent_id)

        expected_name = f'{CallableClass.__qualname__}.__call__'
        string_handle_class_mock.assert_called_once_with(expected_name)

        self.assertEqual(task.name(), expected_name)
        self.assertEqual(task.domain(), domain_name)
        self.assertEqual(task.id(), task_id)
        self.assertEqual(task.parent_id(), parent_id)

        self.assertEqual(str(task), f"{{ name: '{str(expected_name)}', domain: '{str(domain_name)}',"
                                    f" id: {str(task_id)}, parent_id: {str(parent_id)} }}")

        self.assertEqual(repr(task), f'{task.__class__.__qualname__}({repr(expected_name)}, {repr(domain_name)},'
                                     f' {repr(task_id)}, {repr(parent_id)})')


class TaskExecutionTests(TestCase):
    @pyitt_native_patch('Domain')
    @pyitt_native_patch('Id')
    @pyitt_native_patch('StringHandle')
    @pyitt_native_patch('task_begin')
    @pyitt_native_patch('task_end')
    def test_task_for_function(self, domain_class_mock, id_class_mock, string_handle_class_mock, task_begin_mock,
                               task_end_mock):
        domain_class_mock.return_value = 'domain_handle'
        string_handle_class_mock.return_value = 'string_handle'
        id_class_mock.return_value = 'id_handle'

        @ittapi.task
        def my_function():
            return 42

        domain_class_mock.assert_called_once_with(None)
        string_handle_class_mock.assert_called_once_with(my_function.__qualname__)
        id_class_mock.assert_called_once_with(domain_class_mock.return_value)

        self.assertEqual(my_function(), 42)

        task_begin_mock.assert_called_once_with(domain_class_mock.return_value, string_handle_class_mock.return_value,
                                                id_class_mock.return_value, None)
        task_end_mock.assert_called_once_with(domain_class_mock.return_value)


class NestedTaskCreationTests(TestCase):
    @pyitt_native_patch('Domain')
    @pyitt_native_patch('StringHandle')
    def test_task_creation_with_default_constructor(self, domain_class_mock, string_handle_class_mock):
        ittapi.nested_task()
        caller = stack()[0]
        string_handle_class_mock.assert_called_once_with(f'{basename(caller.filename)}:{caller.lineno-1}')
        domain_class_mock.assert_called_once_with(None)

    @pyitt_native_patch('StringHandle')
    def test_task_creation_with_first_named_argument(self, string_handle_class_mock):
        name = 'my task'
        ittapi.nested_task(task=name)
        string_handle_class_mock.assert_called_once_with(name)


class OverlappedTaskCreationTests(TestCase):
    @pyitt_native_patch('Domain')
    @pyitt_native_patch('StringHandle')
    def test_task_creation_with_default_constructor(self, domain_class_mock, string_handle_class_mock):
        ittapi.overlapped_task()
        caller = stack()[0]
        string_handle_class_mock.assert_called_once_with(f'{basename(caller.filename)}:{caller.lineno-1}')
        domain_class_mock.assert_called_once_with(None)

    @pyitt_native_patch('StringHandle')
    def test_task_creation_with_first_named_argument(self, string_handle_class_mock):
        name = 'my task'
        ittapi.overlapped_task(task=name)
        string_handle_class_mock.assert_called_once_with(name)


class OverlappedTaskExecution(TestCase):
    @pyitt_native_patch('Domain')
    @pyitt_native_patch('Id')
    @pyitt_native_patch('StringHandle')
    @pyitt_native_patch('task_begin_overlapped')
    @pyitt_native_patch('task_end_overlapped')
    def test_overlapped_tasks(self, domain_class_mock, id_class_mock, string_handle_class_mock,
                              task_begin_overlapped_mock, task_end_overlapped_mock):
        domain_class_mock.return_value = 'domain_handle'
        string_handle_class_mock.side_effect = lambda x: x

        id_value = 0

        def id_generator(*args, **kwargs):  # pylint: disable=W0613
            nonlocal id_value
            id_value += 1
            return id_value

        id_class_mock.side_effect = id_generator

        overlapped_task_1_name = 'overlapped task 1'
        overlapped_task_2_name = 'overlapped task 2'

        overlapped_task_1 = ittapi.overlapped_task(overlapped_task_1_name)
        overlapped_task_1.begin()

        overlapped_task_2 = ittapi.overlapped_task(overlapped_task_2_name)
        overlapped_task_2.begin()

        overlapped_task_1.end()
        overlapped_task_2.end()

        expected_calls = [
            call(overlapped_task_1_name),
            call(overlapped_task_2_name)
        ]
        string_handle_class_mock.assert_has_calls(expected_calls)

        expected_calls = [
            call(domain_class_mock.return_value, overlapped_task_1_name, 1, None),
            call(domain_class_mock.return_value, overlapped_task_2_name, 2, None)
        ]
        task_begin_overlapped_mock.assert_has_calls(expected_calls)

        expected_calls = [
            call(domain_class_mock.return_value, 1),
            call(domain_class_mock.return_value, 2)
        ]
        task_end_overlapped_mock.assert_has_calls(expected_calls)


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
