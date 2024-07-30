from inspect import stack
from os.path import basename
from unittest import main as unittest_main, TestCase
from unittest.mock import call

from ...pyitt_native_mock import patch as pyitt_native_patch
import pyitt.compatibility_layers.ittapi as ittapi  # pylint: disable=C0411


class EventCreationTests(TestCase):
    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_creation_with_default_constructor(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        event = ittapi.event()
        caller = stack()[0]
        expected_name = f'{basename(caller.filename)}:{caller.lineno-1}'

        event_class_mock.assert_not_called()

        event.begin()

        event_class_mock.assert_called_once_with(expected_name)
        self.assertEqual(event.name(), expected_name)

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_creation_as_decorator_for_function(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        @ittapi.event
        def my_function():
            pass  # pragma: no cover

        event_class_mock.assert_called_once_with(my_function.__qualname__)

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_creation_as_decorator_with_name_for_function(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        @ittapi.event('my function')
        def my_function():
            pass  # pragma: no cover

        event_class_mock.assert_called_once_with('my function')

    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_creation_for_method(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        class MyClass:
            @ittapi.event
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

        event = ittapi.event(CallableClass())

        expected_name = f'{CallableClass.__qualname__}.__call__'
        event_class_mock.assert_called_once_with(expected_name)

        self.assertEqual(event.name(), expected_name)

        self.assertEqual(str(event), expected_name)
        self.assertEqual(repr(event), f'{event.__class__.__qualname__}(\'{expected_name}\')')


class EventExecutionTests(TestCase):
    @pyitt_native_patch('Event')
    @pyitt_native_patch('StringHandle')
    def test_event_for_function(self, event_class_mock, string_handle_class_mock):
        string_handle_class_mock.return_value = 'string_handle'

        @ittapi.event
        def my_function():
            return 42

        string_handle_class_mock.assert_called_once_with(my_function.__qualname__)
        event_class_mock.assert_called_once_with(string_handle_class_mock.return_value)

        self.assertEqual(my_function(), 42)

        expected_calls = [call().begin(),
                          call().end()]
        event_class_mock.assert_has_calls(expected_calls)


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
