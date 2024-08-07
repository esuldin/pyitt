from inspect import stack
from os.path import basename
from unittest import main as unittest_main, TestCase
from unittest.mock import call

from .pyitt_native_mock import patch as pyitt_native_patch
import pyitt  # pylint: disable=C0411


class EventCreationTests(TestCase):
    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_creation_with_default_constructor(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        event = pyitt.event()
        caller = stack()[0]
        expected_name = f'{basename(caller.filename)}:{caller.lineno-1}'

        event_class_mock.assert_not_called()

        event.begin()

        event_class_mock.assert_called_once_with(expected_name)
        self.assertEqual(event.name, expected_name)

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_creation_as_decorator_for_function(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        @pyitt.event
        def my_function():
            pass  # pragma: no cover

        event_class_mock.assert_called_once_with(my_function.__qualname__)

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_creation_as_decorator_with_empty_arguments_for_function(self, event_class_mock,
                                                                           string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        @pyitt.event()
        def my_function():
            pass  # pragma: no cover

        event_class_mock.assert_called_with(my_function.__qualname__)

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_creation_as_decorator_with_name_for_function(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        @pyitt.event('my function')
        def my_function():
            pass  # pragma: no cover

        event_class_mock.assert_called_once_with('my function')

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_creation_as_decorator_with_empty_args_and_name_for_function(self, event_class_mock,
                                                                               string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        @pyitt.event
        @pyitt.event('my function')
        def my_function():
            pass  # pragma: no cover

        expected_calls = [call('my function'),
                          call(my_function.__qualname__)]
        event_class_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_creation_with_default_constructor_as_context_manager(self, event_class_mock,
                                                                        string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        caller = stack()[0]
        with pyitt.event():
            pass

        event_class_mock.assert_called_once_with(f'{basename(caller.filename)}:{caller.lineno+1}')

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_creation_with_name_and_domain_as_context_manager(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        with pyitt.event('my event'):
            pass

        event_class_mock.assert_called_once_with('my event')

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_creation_for_callable_object(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        class CallableClass:
            def __call__(self, *args, **kwargs):
                pass  # pragma: no cover

        event = pyitt.event(CallableClass())

        expected_name = f'{CallableClass.__qualname__}.__call__'
        event_class_mock.assert_called_once_with(expected_name)

        self.assertEqual(event.name, expected_name)

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_unnamed_event_creation_for_callable_object(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        class CallableClass:
            def __call__(self, *args, **kwargs):
                pass  # pragma: no cover

        event = pyitt.event()
        event(CallableClass())

        expected_name = f'{CallableClass.__qualname__}.__call__'
        event_class_mock.assert_called_once_with(expected_name)
        self.assertEqual(event.name, expected_name)

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_creation_for_method(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        class MyClass:
            @pyitt.event
            def my_method(self):
                pass  # pragma: no cover

        event_class_mock.assert_called_once_with(f'{MyClass.my_method.__qualname__}')


class EventPropertiesTest(TestCase):
    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_properties(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        class CallableClass:
            def __call__(self, *args, **kwargs):
                pass  # pragma: no cover

        event = pyitt.event(CallableClass())

        expected_name = f'{CallableClass.__qualname__}.__call__'
        event_class_mock.assert_called_once_with(expected_name)

        self.assertEqual(event.name, expected_name)

        self.assertEqual(str(event), expected_name)
        self.assertEqual(repr(event), f'{event.__class__.__qualname__}(\'{expected_name}\')')


class EventExecutionTests(TestCase):
    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_for_function(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.return_value = 'string_handle'

        @pyitt.event
        def my_function():
            return 42

        string_handle_class_mock.assert_called_once_with(my_function.__qualname__)
        event_class_mock.assert_called_once_with(string_handle_class_mock.return_value)

        self.assertEqual(my_function(), 42)

        expected_calls = [call().begin(),
                          call().end()]
        event_class_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_nested_events_for_function(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        @pyitt.event
        @pyitt.event('my function')
        def my_function():
            return 42

        expected_calls = [call('my function'),
                          call(my_function.__qualname__)]
        string_handle_class_mock.assert_has_calls(expected_calls)
        event_class_mock.assert_has_calls(expected_calls)

        self.assertEqual(my_function(), 42)

        expected_calls = [call().begin(),
                          call().begin(),
                          call().end(),
                          call().end()]
        event_class_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_as_context_manager(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        region_name = 'my region'
        with pyitt.event(region_name):
            pass

        string_handle_class_mock.assert_called_once_with(region_name)
        event_class_mock.assert_called_once_with(region_name)

        expected_calls = [call().begin(),
                          call().end()]
        event_class_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_for_callable_object(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.return_value = 'string_handle'

        class CallableClass:
            def __call__(self, *args, **kwargs):
                return 42

        callable_object = pyitt.event(CallableClass())
        string_handle_class_mock.assert_called_once_with(f'{CallableClass.__qualname__}.__call__')
        event_class_mock.assert_called_once_with(string_handle_class_mock.return_value)

        self.assertEqual(callable_object(), 42)

        expected_calls = [call().begin(),
                          call().end()]
        event_class_mock.assert_has_calls(expected_calls)

    def test_event_for_multiple_callable_objects(self):
        class CallableClass:
            def __call__(self, *args, **kwargs):
                return 42

        event = pyitt.event()
        wrapped_object = event(CallableClass())

        self.assertEqual(wrapped_object, event)
        self.assertEqual(event(), 42)

    def test_event_for_noncallable_object(self):
        with self.assertRaises(TypeError) as context:
            pyitt.event()(42)

        self.assertEqual(str(context.exception), 'Callable object or method descriptor are expected to be passed.')

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_for_method(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        class MyClass:
            @pyitt.event
            def my_method(self):
                return 42

        string_handle_class_mock.assert_called_once_with(f'{MyClass.my_method.__qualname__}')
        event_class_mock.assert_called_once_with(f'{MyClass.my_method.__qualname__}')

        my_object = MyClass()
        self.assertEqual(my_object.my_method(), 42)

        expected_calls = [call().begin(),
                          call().end()]
        event_class_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_for_class_method(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        class MyClass:
            @classmethod
            @pyitt.event
            def my_class_method(cls):
                return 42

        string_handle_class_mock.assert_called_once_with(f'{MyClass.my_class_method.__qualname__}')
        event_class_mock.assert_called_once_with(f'{MyClass.my_class_method.__qualname__}')

        self.assertEqual(MyClass.my_class_method(), 42)

        expected_calls = [call().begin(),
                          call().end()]
        event_class_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_for_static_method(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        class MyClass:
            @staticmethod
            @pyitt.event
            def my_static_method():
                return 42

        string_handle_class_mock.assert_called_once_with(f'{MyClass.my_static_method.__qualname__}')
        event_class_mock.assert_called_once_with(f'{MyClass.my_static_method.__qualname__}')

        self.assertEqual(MyClass.my_static_method(), 42)
        self.assertEqual(MyClass().my_static_method(), 42)

        expected_calls = [call().begin(),
                          call().end(),
                          call().begin(),
                          call().end()]
        event_class_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_for_function_raised_exception(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.return_value = 'string_handle'

        exception_msg = 'ValueError exception from my_function'

        @pyitt.event
        def my_function():
            raise ValueError(exception_msg)

        string_handle_class_mock.assert_called_once_with(my_function.__qualname__)
        event_class_mock.assert_called_once_with(string_handle_class_mock.return_value)

        with self.assertRaises(ValueError) as context:
            my_function()

        self.assertEqual(str(context.exception), exception_msg)

        expected_calls = [call().begin(),
                          call().end()]
        event_class_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_for_method_raised_exception(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        exception_msg = 'ValueError exception from my_method'

        class MyClass:
            @pyitt.event
            def my_method(self):
                raise ValueError(exception_msg)

        string_handle_class_mock.assert_called_once_with(f'{MyClass.my_method.__qualname__}')
        event_class_mock.assert_called_once_with(f'{MyClass.my_method.__qualname__}')

        with self.assertRaises(ValueError) as context:
            MyClass().my_method()

        self.assertEqual(str(context.exception), exception_msg)

        expected_calls = [call().begin(),
                          call().end()]
        event_class_mock.assert_has_calls(expected_calls)


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
