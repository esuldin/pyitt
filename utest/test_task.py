from inspect import stack
from os.path import basename
from unittest import main as unittest_main, skip, TestCase
from unittest.mock import call

from pyitt_native_mock import patch as pyitt_native_patch
import pyitt


class TaskCreationTests(TestCase):
    @pyitt_native_patch('Domain')
    @pyitt_native_patch('StringHandle')
    def test_task_creation_with_default_constructor(self, domain_mock, string_handle_mock):
        task = pyitt.task()
        caller = stack()[0]
        string_handle_mock.assert_called_once_with(f'{basename(caller.filename)}:{caller.lineno-1}')
        domain_mock.assert_called_once_with(None)

    @pyitt_native_patch('StringHandle')
    def test_task_creation_as_decorator_for_function(self, string_handle_mock):
        @pyitt.task
        def my_function():
            pass  # pragma: no cover

        string_handle_mock.assert_called_once_with(my_function.__qualname__)

    @pyitt_native_patch('StringHandle')
    def test_task_creation_as_decorator_with_empty_arguments_for_function(self, string_handle_mock):
        @pyitt.task()
        def my_function():
            pass  # pragma: no cover

        string_handle_mock.assert_called_with(my_function.__qualname__)

    @pyitt_native_patch('StringHandle')
    def test_task_creation_as_decorator_with_name_for_function(self, string_handle_mock):
        @pyitt.task('my function')
        def my_function():
            pass  # pragma: no cover

        string_handle_mock.assert_called_once_with('my function')

    @pyitt_native_patch('Domain')
    def test_task_creation_as_decorator_with_domain_for_function(self, domain_mock):
        @pyitt.task(domain='my domain')
        def my_function():
            pass  # pragma: no cover

        domain_mock.assert_called_once_with('my domain')

    @pyitt_native_patch('StringHandle')
    def test_task_creation_as_decorator_with_empty_args_and_name_for_function(self, string_handle_mock):
        @pyitt.task
        @pyitt.task('my function')
        def my_function():
            pass  # pragma: no cover

        expected_calls = [call('my function'),
                          call(my_function.__qualname__)]
        string_handle_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('StringHandle')
    def test_task_creation_with_default_constructor_as_context_manager(self, domain_mock, string_handle_mock):
        caller = stack()[0]
        with pyitt.task():
            pass

        string_handle_mock.assert_called_once_with(f'{basename(caller.filename)}:{caller.lineno+1}')
        domain_mock.assert_called_once_with(None)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('StringHandle')
    def test_task_creation_with_name_and_domain_as_context_manager(self, domain_mock, string_handle_mock):
        with pyitt.task('my task', 'my domain'):
            pass

        string_handle_mock.assert_called_once_with('my task')
        domain_mock.assert_called_once_with('my domain')

    @pyitt_native_patch('StringHandle')
    def test_task_creation_for_callable_object(self, string_handle_mock):
        class CallableClass:
            def __call__(self, *args, **kwargs):
                pass  # pragma: no cover

        pyitt.task(CallableClass())
        string_handle_mock.assert_called_once_with(f'{CallableClass.__name__}.__call__')

    @pyitt_native_patch('StringHandle')
    def test_task_creation_for_method(self, string_handle_mock):
        class MyClass:
            @pyitt.task
            def my_method(self):
                pass  # pragma: no cover

        string_handle_mock.assert_called_once_with(f'{MyClass.my_method.__qualname__}')


class TaskExecutionTests(TestCase):
    @pyitt_native_patch('Domain')
    @pyitt_native_patch('Id')
    @pyitt_native_patch('StringHandle')
    @pyitt_native_patch('task_begin')
    @pyitt_native_patch('task_end')
    def test_task_for_function(self, domain_mock, id_mock, string_handle_mock, task_begin_mock, task_end_mock):
        domain_mock.return_value = 'domain_handle'
        string_handle_mock.return_value = 'string_handle'
        id_mock.return_value = 'id_handle'

        @pyitt.task
        def my_function():
            pass

        domain_mock.assert_called_once_with(None)
        string_handle_mock.assert_called_once_with(my_function.__qualname__)
        id_mock.assert_called_once_with(domain_mock.return_value)

        my_function()

        task_begin_mock.assert_called_once_with(domain_mock.return_value, string_handle_mock.return_value,
                                                id_mock.return_value, None)
        task_end_mock.assert_called_once_with(domain_mock.return_value)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('Id')
    @pyitt_native_patch('StringHandle')
    @pyitt_native_patch('task_begin')
    @pyitt_native_patch('task_end')
    def test_nested_tasks_for_function(self, domain_mock, id_mock, string_handle_mock, task_begin_mock, task_end_mock):
        domain_mock.return_value = 'domain_handle'
        string_handle_mock.side_effect = lambda x: x
        id_mock.return_value = 'id_handle'

        @pyitt.task
        @pyitt.task('my function')
        def my_function():
            pass

        expected_calls = [call('my function'),
                          call(my_function.__qualname__)]
        string_handle_mock.assert_has_calls(expected_calls)

        my_function()

        expected_calls = [call(domain_mock.return_value, my_function.__qualname__, id_mock.return_value, None),
                          call(domain_mock.return_value, 'my function', id_mock.return_value, None)]
        task_begin_mock.assert_has_calls(expected_calls)

        expected_calls = [call(domain_mock.return_value),
                          call(domain_mock.return_value)]
        task_end_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('Id')
    @pyitt_native_patch('StringHandle')
    @pyitt_native_patch('task_begin')
    @pyitt_native_patch('task_end')
    def test_task_as_context_manager(self, domain_mock, id_mock, string_handle_mock, task_begin_mock, task_end_mock):
        domain_mock.return_value = 'domain_handle'
        string_handle_mock.side_effect = lambda x: x
        id_mock.return_value = 'id_handle'

        region_name = 'my region'
        with pyitt.task(region_name):
            pass

        domain_mock.assert_called_once_with(None)
        string_handle_mock.assert_called_once_with(region_name)
        id_mock.assert_called_once_with(domain_mock.return_value)

        task_begin_mock.assert_called_once_with(domain_mock.return_value, region_name, id_mock.return_value, None)
        task_end_mock.assert_called_once_with(domain_mock.return_value)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('Id')
    @pyitt_native_patch('StringHandle')
    @pyitt_native_patch('task_begin')
    @pyitt_native_patch('task_end')
    def test_task_for_callable_object(self, domain_mock, id_mock, string_handle_mock, task_begin_mock, task_end_mock):
        domain_mock.return_value = 'domain_handle'
        string_handle_mock.return_value = 'string_handle'
        id_mock.return_value = 'id_handle'

        class CallableClass:
            def __call__(self, *args, **kwargs):
                pass

        callable_object = pyitt.task(CallableClass())
        string_handle_mock.assert_called_once_with(f'{CallableClass.__name__}.__call__')

        callable_object()

        task_begin_mock.assert_called_once_with(domain_mock.return_value, string_handle_mock.return_value,
                                                id_mock.return_value, None)
        task_end_mock.assert_called_once_with(domain_mock.return_value)

    @skip
    @pyitt_native_patch('Domain')
    @pyitt_native_patch('Id')
    @pyitt_native_patch('StringHandle')
    @pyitt_native_patch('task_begin')
    @pyitt_native_patch('task_end')
    def test_task_for_method(self, domain_mock, id_mock, string_handle_mock, task_begin_mock, task_end_mock):
        domain_mock.return_value = 'domain_handle'
        string_handle_mock.return_value = 'string_handle'
        id_mock.return_value = 'id_handle'

        class MyClass:
            @pyitt.task
            def my_method(self):
                pass

        string_handle_mock.assert_called_once_with(f'{MyClass.my_method.__qualname__}')

        my_object = MyClass()
        my_object.my_method()

        task_begin_mock.assert_called_once_with(domain_mock.return_value, string_handle_mock.return_value,
                                                id_mock.return_value, None)
        task_end_mock.assert_called_once_with(domain_mock.return_value)


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
