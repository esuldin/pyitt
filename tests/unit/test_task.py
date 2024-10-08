from inspect import stack
from os.path import basename
from unittest import main as unittest_main, TestCase
from unittest.mock import call, Mock

# pylint: disable=C0411
from .pyitt_native_mock import patch as pyitt_native_patch
from pyitt.task import _Task
import pyitt


class TaskAbstractMethodsTest(TestCase):
    def test_region_abstract_method_begin(self):
        with self.assertRaises(NotImplementedError):
            _Task.begin(_Task())

    def test_region_abstract_method_end(self):
        with self.assertRaises(NotImplementedError):
            _Task.end(_Task())


class TaskCreationTests(TestCase):
    @pyitt_native_patch('Domain')
    @pyitt_native_patch('StringHandle')
    @pyitt_native_patch('Id')
    def test_task_creation_with_default_constructor(self, domain_class_mock, string_handle_class_mock, id_class_mock):
        domain_class_mock.return_value = 'pyitt'
        string_handle_class_mock.side_effect = lambda x: x
        id_class_mock.return_value = 1

        task = pyitt.task()
        caller = stack()[0]
        expected_name = f'{basename(caller.filename)}:{caller.lineno-1}'

        string_handle_class_mock.assert_called_once_with(expected_name)
        domain_class_mock.assert_called_once_with(None)

        self.assertEqual(task.name, expected_name)
        self.assertEqual(task.domain, domain_class_mock.return_value)
        self.assertEqual(task.id, id_class_mock.return_value)
        self.assertIsNone(task.parent_id)

    @pyitt_native_patch('StringHandle')
    def test_task_creation_as_decorator_for_function(self, string_handle_class_mock):
        @pyitt.task
        def my_function():
            pass  # pragma: no cover

        string_handle_class_mock.assert_called_once_with(my_function.__qualname__)

    @pyitt_native_patch('StringHandle')
    def test_task_creation_as_decorator_with_empty_arguments_for_function(self, string_handle_class_mock):
        @pyitt.task()
        def my_function():
            pass  # pragma: no cover

        string_handle_class_mock.assert_called_with(my_function.__qualname__)

    @pyitt_native_patch('StringHandle')
    def test_task_creation_as_decorator_with_name_for_function(self, string_handle_class_mock):
        @pyitt.task('my function')
        def my_function():
            pass  # pragma: no cover

        string_handle_class_mock.assert_called_once_with('my function')

    @pyitt_native_patch('Domain')
    def test_task_creation_as_decorator_with_domain_for_function(self, domain_class_mock):
        @pyitt.task(domain='my domain')
        def my_function():
            pass  # pragma: no cover

        domain_class_mock.assert_called_once_with('my domain')

    @pyitt_native_patch('StringHandle')
    def test_task_creation_as_decorator_with_empty_args_and_name_for_function(self, string_handle_class_mock):
        @pyitt.task
        @pyitt.task('my function')
        def my_function():
            pass  # pragma: no cover

        expected_calls = [call('my function'),
                          call(my_function.__qualname__)]
        string_handle_class_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('StringHandle')
    def test_task_creation_with_default_constructor_as_context_manager(self, domain_class_mock,
                                                                       string_handle_class_mock):
        caller = stack()[0]
        with pyitt.task():
            pass

        string_handle_class_mock.assert_called_once_with(f'{basename(caller.filename)}:{caller.lineno+1}')
        domain_class_mock.assert_called_once_with(None)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('StringHandle')
    def test_task_creation_with_name_and_domain_as_context_manager(self, domain_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        task_name = 'my task'
        with pyitt.task(task_name, 'my domain') as task:
            self.assertEqual(task.name, task_name)

        string_handle_class_mock.assert_called_once_with('my task')
        domain_class_mock.assert_called_once_with('my domain')

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('StringHandle')
    def test_task_creation_with_domain_object_as_context_manager(self, domain_class_mock, string_handle_class_mock):
        domain_mock = Mock()

        with pyitt.task(domain=domain_mock) as task:
            self.assertEqual(task.domain, domain_mock)

        string_handle_class_mock.assert_called_once()
        domain_class_mock.assert_not_called()

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('Id')
    @pyitt_native_patch('StringHandle')
    def test_task_creation_for_callable_object(self, domain_class_mock, id_class_mock, string_handle_class_mock):
        domain_class_mock.return_value = 'domain'
        string_handle_class_mock.side_effect = lambda x: x
        id_class_mock.return_value = 1

        class CallableClass:
            def __call__(self, *args, **kwargs):
                pass  # pragma: no cover

        task = pyitt.task(CallableClass())

        expected_name = f'{CallableClass.__qualname__}.__call__'
        string_handle_class_mock.assert_called_once_with(expected_name)

        self.assertEqual(task.name, expected_name)
        self.assertEqual(task.domain, domain_class_mock.return_value)
        self.assertEqual(task.id, id_class_mock.return_value)
        self.assertIsNone(task.parent_id)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('Id')
    @pyitt_native_patch('StringHandle')
    def test_unnamed_task_creation_for_callable_object(self, domain_class_mock, id_class_mock,
                                                       string_handle_class_mock):
        domain_class_mock.return_value = 'domain'
        string_handle_class_mock.side_effect = lambda x: x
        id_class_mock.return_value = 1

        class CallableClass:
            def __call__(self, *args, **kwargs):
                pass  # pragma: no cover

        caller = stack()[0]
        task = pyitt.task()
        task(CallableClass())

        expected_name = f'{CallableClass.__qualname__}.__call__'
        expected_calls = [
            call(f'{basename(caller.filename)}:{caller.lineno+1}'),
            call(expected_name)
        ]
        string_handle_class_mock.assert_has_calls(expected_calls)

        self.assertEqual(task.name, expected_name)
        self.assertEqual(task.domain, domain_class_mock.return_value)
        self.assertEqual(task.id, id_class_mock.return_value)
        self.assertIsNone(task.parent_id)

    @pyitt_native_patch('StringHandle')
    def test_task_creation_for_method(self, string_handle_class_mock):
        class MyClass:
            @pyitt.task
            def my_method(self):
                pass  # pragma: no cover

        string_handle_class_mock.assert_called_once_with(f'{MyClass.my_method.__qualname__}')

    def test_task_creation_with_first_named_argument(self):
        with self.assertRaises(TypeError) as context:
            pyitt.task(task='my task')  # pylint: disable=E3102

        self.assertRegex(str(context.exception), r"task\(\) got \w+ positional-only argument\w? passed"
                                                 r" as keyword argument\w?: 'task'")


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
        task = pyitt.task(CallableClass(), domain=domain_name, id=task_id, parent=parent_id)

        expected_name = f'{CallableClass.__qualname__}.__call__'
        string_handle_class_mock.assert_called_once_with(expected_name)

        self.assertEqual(task.name, expected_name)
        self.assertEqual(task.domain, domain_name)
        self.assertEqual(task.id, task_id)
        self.assertEqual(task.parent_id, parent_id)

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

        @pyitt.task
        def my_function():
            return 42

        domain_class_mock.assert_called_once_with(None)
        string_handle_class_mock.assert_called_once_with(my_function.__qualname__)
        id_class_mock.assert_called_once_with(domain_class_mock.return_value)

        self.assertEqual(my_function(), 42)

        task_begin_mock.assert_called_once_with(domain_class_mock.return_value, string_handle_class_mock.return_value,
                                                id_class_mock.return_value, None)
        task_end_mock.assert_called_once_with(domain_class_mock.return_value)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('Id')
    @pyitt_native_patch('StringHandle')
    @pyitt_native_patch('task_begin')
    @pyitt_native_patch('task_end')
    def test_nested_tasks_for_function(self, domain_class_mock, id_class_mock, string_handle_class_mock,
                                       task_begin_mock, task_end_mock):
        domain_class_mock.return_value = 'domain_handle'
        string_handle_class_mock.side_effect = lambda x: x
        id_class_mock.return_value = 'id_handle'

        @pyitt.task
        @pyitt.task('my function')
        def my_function():
            return 42

        expected_calls = [call('my function'),
                          call(my_function.__qualname__)]
        string_handle_class_mock.assert_has_calls(expected_calls)

        self.assertEqual(my_function(), 42)

        expected_calls = [
            call(domain_class_mock.return_value, my_function.__qualname__, id_class_mock.return_value, None),
            call(domain_class_mock.return_value, 'my function', id_class_mock.return_value, None)
        ]
        task_begin_mock.assert_has_calls(expected_calls)

        expected_calls = [call(domain_class_mock.return_value),
                          call(domain_class_mock.return_value)]
        task_end_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('Id')
    @pyitt_native_patch('StringHandle')
    @pyitt_native_patch('task_begin')
    @pyitt_native_patch('task_end')
    def test_task_as_context_manager(self, domain_class_mock, id_class_mock, string_handle_class_mock, task_begin_mock,
                                     task_end_mock):
        domain_class_mock.return_value = 'domain_handle'
        string_handle_class_mock.side_effect = lambda x: x
        id_class_mock.return_value = 'id_handle'

        task_name = 'my task'
        with pyitt.task(task_name) as task:
            self.assertEqual(task.name, task_name)

        domain_class_mock.assert_called_once_with(None)
        string_handle_class_mock.assert_called_once_with(task_name)
        id_class_mock.assert_called_once_with(domain_class_mock.return_value)

        task_begin_mock.assert_called_once_with(domain_class_mock.return_value, task_name, id_class_mock.return_value,
                                                None)
        task_end_mock.assert_called_once_with(domain_class_mock.return_value)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('Id')
    @pyitt_native_patch('StringHandle')
    @pyitt_native_patch('task_begin')
    @pyitt_native_patch('task_end')
    def test_task_for_callable_object(self, domain_class_mock, id_class_mock, string_handle_class_mock, task_begin_mock,
                                      task_end_mock):
        domain_class_mock.return_value = 'domain_handle'
        string_handle_class_mock.return_value = 'string_handle'
        id_class_mock.return_value = 'id_handle'

        class CallableClass:
            def __call__(self, *args, **kwargs):
                return 42

        callable_object = pyitt.task(CallableClass())
        string_handle_class_mock.assert_called_once_with(f'{CallableClass.__qualname__}.__call__')

        self.assertEqual(callable_object(), 42)

        task_begin_mock.assert_called_once_with(domain_class_mock.return_value, string_handle_class_mock.return_value,
                                                id_class_mock.return_value, None)
        task_end_mock.assert_called_once_with(domain_class_mock.return_value)

    def test_task_for_multiple_calls(self):
        class CallableClass:
            def __call__(self, *args, **kwargs):
                return 42

        task = pyitt.task()
        wrapped_object = task(CallableClass())

        self.assertEqual(wrapped_object, task)
        self.assertEqual(task(), 42)

    def test_task_for_noncallable_object(self):
        with self.assertRaises(TypeError) as context:
            pyitt.task()(42)

        self.assertEqual(str(context.exception), 'Callable object or method descriptor are expected to be passed.')

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('Id')
    @pyitt_native_patch('StringHandle')
    @pyitt_native_patch('task_begin')
    @pyitt_native_patch('task_end')
    def test_task_for_method(self, domain_class_mock, id_class_mock, string_handle_class_mock, task_begin_mock,
                             task_end_mock):
        domain_class_mock.return_value = 'domain_handle'
        string_handle_class_mock.side_effect = lambda x: x
        id_class_mock.return_value = 'id_handle'

        class MyClass:
            @pyitt.task
            def my_method(self):
                return 42

        string_handle_class_mock.assert_called_once_with(f'{MyClass.my_method.__qualname__}')

        my_object = MyClass()
        self.assertEqual(my_object.my_method(), 42)

        task_begin_mock.assert_called_once_with(domain_class_mock.return_value, f'{MyClass.my_method.__qualname__}',
                                                id_class_mock.return_value, None)
        task_end_mock.assert_called_once_with(domain_class_mock.return_value)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('Id')
    @pyitt_native_patch('StringHandle')
    @pyitt_native_patch('task_begin')
    @pyitt_native_patch('task_end')
    def test_task_for_class_method(self, domain_class_mock, id_class_mock, string_handle_class_mock, task_begin_mock,
                                   task_end_mock):
        domain_class_mock.return_value = 'domain_handle'
        string_handle_class_mock.side_effect = lambda x: x
        id_class_mock.return_value = 'id_handle'

        class MyClass:
            @classmethod
            @pyitt.task
            def my_class_method(cls):
                return 42

        string_handle_class_mock.assert_called_once_with(f'{MyClass.my_class_method.__qualname__}')

        self.assertEqual(MyClass.my_class_method(), 42)

        task_begin_mock.assert_called_once_with(domain_class_mock.return_value,
                                                f'{MyClass.my_class_method.__qualname__}',
                                                id_class_mock.return_value, None)
        task_end_mock.assert_called_once_with(domain_class_mock.return_value)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('Id')
    @pyitt_native_patch('StringHandle')
    @pyitt_native_patch('task_begin')
    @pyitt_native_patch('task_end')
    def test_task_for_static_method(self, domain_class_mock, id_class_mock, string_handle_class_mock, task_begin_mock,
                                    task_end_mock):
        domain_class_mock.return_value = 'domain_handle'
        string_handle_class_mock.side_effect = lambda x: x
        id_class_mock.return_value = 'id_handle'

        class MyClass:
            @staticmethod
            @pyitt.task
            def my_static_method():
                return 42

        string_handle_class_mock.assert_called_once_with(f'{MyClass.my_static_method.__qualname__}')

        self.assertEqual(MyClass.my_static_method(), 42)

        task_begin_mock.assert_called_once_with(domain_class_mock.return_value,
                                                f'{MyClass.my_static_method.__qualname__}',
                                                id_class_mock.return_value, None)
        task_end_mock.assert_called_once_with(domain_class_mock.return_value)

        task_begin_mock.reset_mock()
        task_end_mock.reset_mock()

        self.assertEqual(MyClass().my_static_method(), 42)

        task_begin_mock.assert_called_once_with(domain_class_mock.return_value,
                                                f'{MyClass.my_static_method.__qualname__}',
                                                id_class_mock.return_value, None)
        task_end_mock.assert_called_once_with(domain_class_mock.return_value)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('Id')
    @pyitt_native_patch('StringHandle')
    @pyitt_native_patch('task_begin')
    @pyitt_native_patch('task_end')
    def test_task_for_function_raised_exception(self, domain_class_mock, id_class_mock, string_handle_class_mock,
                                                task_begin_mock, task_end_mock):
        domain_class_mock.return_value = 'domain_handle'
        string_handle_class_mock.return_value = 'string_handle'
        id_class_mock.return_value = 'id_handle'

        exception_msg = 'ValueError exception from my_function'

        @pyitt.task
        def my_function():
            raise ValueError(exception_msg)

        domain_class_mock.assert_called_once_with(None)
        string_handle_class_mock.assert_called_once_with(my_function.__qualname__)
        id_class_mock.assert_called_once_with(domain_class_mock.return_value)

        with self.assertRaises(ValueError) as context:
            my_function()

        self.assertEqual(str(context.exception), exception_msg)

        task_begin_mock.assert_called_once_with(domain_class_mock.return_value, string_handle_class_mock.return_value,
                                                id_class_mock.return_value, None)
        task_end_mock.assert_called_once_with(domain_class_mock.return_value)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('Id')
    @pyitt_native_patch('StringHandle')
    @pyitt_native_patch('task_begin')
    @pyitt_native_patch('task_end')
    def test_task_for_method_raised_exception(self, domain_class_mock, id_class_mock, string_handle_class_mock,
                                              task_begin_mock, task_end_mock):
        domain_class_mock.return_value = 'domain_handle'
        string_handle_class_mock.side_effect = lambda x: x
        id_class_mock.return_value = 'id_handle'

        exception_msg = 'ValueError exception from my_method'

        class MyClass:
            @pyitt.task
            def my_method(self):
                raise ValueError(exception_msg)

        string_handle_class_mock.assert_called_once_with(f'{MyClass.my_method.__qualname__}')

        with self.assertRaises(ValueError) as context:
            MyClass().my_method()

        self.assertEqual(str(context.exception), exception_msg)

        task_begin_mock.assert_called_once_with(domain_class_mock.return_value, f'{MyClass.my_method.__qualname__}',
                                                id_class_mock.return_value, None)
        task_end_mock.assert_called_once_with(domain_class_mock.return_value)


class NestedTaskCreationTests(TestCase):
    @pyitt_native_patch('Domain')
    @pyitt_native_patch('StringHandle')
    def test_task_creation_with_default_constructor(self, domain_class_mock, string_handle_class_mock):
        pyitt.nested_task()
        caller = stack()[0]
        string_handle_class_mock.assert_called_once_with(f'{basename(caller.filename)}:{caller.lineno-1}')
        domain_class_mock.assert_called_once_with(None)

    def test_task_creation_with_first_named_argument(self):
        with self.assertRaises(TypeError) as context:
            pyitt.nested_task(task='my task')  # pylint: disable=E3102

        self.assertRegex(str(context.exception), r"nested_task\(\) got \w+ positional-only argument\w? passed"
                                                 r" as keyword argument\w?: 'task'")

    def test_task_creation_with_first_named_argument_using_class(self):
        with self.assertRaises(TypeError) as context:
            pyitt.NestedTask(task='my task')  # pylint: disable=E3102

        self.assertRegex(str(context.exception), r"(?:_Task\.)?__init__\(\) got \w+ positional-only argument\w? passed"
                                                 r" as keyword argument\w?: 'task'")


class OverlappedTaskCreationTests(TestCase):
    @pyitt_native_patch('Domain')
    @pyitt_native_patch('StringHandle')
    def test_task_creation_with_default_constructor(self, domain_class_mock, string_handle_class_mock):
        pyitt.overlapped_task()
        caller = stack()[0]
        string_handle_class_mock.assert_called_once_with(f'{basename(caller.filename)}:{caller.lineno-1}')
        domain_class_mock.assert_called_once_with(None)

    def test_task_creation_with_first_named_argument(self):
        with self.assertRaises(TypeError) as context:
            pyitt.overlapped_task(task='my task')  # pylint: disable=E3102

        self.assertRegex(str(context.exception), r"overlapped_task\(\) got \w+ positional-only argument\w? passed"
                                                 r" as keyword argument\w?: 'task'")

    def test_task_creation_with_first_named_argument_using_class(self):
        with self.assertRaises(TypeError) as context:
            pyitt.OverlappedTask(task='my task')  # pylint: disable=E3102

        self.assertRegex(str(context.exception), r"(?:_Task\.)?__init__\(\) got \w+ positional-only argument\w? passed"
                                                 r" as keyword argument\w?: 'task'")


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

        overlapped_task_1 = pyitt.overlapped_task(overlapped_task_1_name)
        overlapped_task_1.begin()

        overlapped_task_2 = pyitt.overlapped_task(overlapped_task_2_name)
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
