from unittest import main as unittest_main, TestCase
from unittest.mock import call, Mock

from .pyitt_native_mock import patch as pyitt_native_patch
import pyitt  # pylint: disable=C0411


class FrameCreationTests(TestCase):
    @pyitt_native_patch('Domain')
    def test_frame_creation_with_default_constructor(self, domain_class_mock):
        domain_class_mock.return_value = 'pyitt'

        frame = pyitt.frame()

        domain_class_mock.assert_called_once_with(None)

        self.assertEqual(frame.domain(), domain_class_mock.return_value)
        self.assertIsNone(frame.id())

    @pyitt_native_patch('Domain')
    def test_frame_creation_as_decorator_for_function(self, domain_class_mock):
        @pyitt.frame
        def my_function():
            pass  # pragma: no cover

        domain_class_mock.assert_called_once_with(None)

    @pyitt_native_patch('Domain')
    def test_frame_creation_as_decorator_with_empty_arguments_for_function(self, domain_class_mock):
        @pyitt.frame()
        def my_function():
            pass  # pragma: no cover

        domain_class_mock.assert_called_once_with(None)

    @pyitt_native_patch('Domain')
    def test_frame_creation_as_decorator_with_domain_for_function(self, domain_class_mock):
        @pyitt.frame(domain='my domain')
        def my_function():
            pass  # pragma: no cover

        domain_class_mock.assert_called_once_with('my domain')

    @pyitt_native_patch('Domain')
    def test_frame_creation_with_default_constructor_as_context_manager(self, domain_class_mock):
        with pyitt.frame():
            pass

        domain_class_mock.assert_called_once_with(None)

    @pyitt_native_patch('Domain')
    def test_frame_creation_with_name_and_domain_as_context_manager(self, domain_class_mock):
        with pyitt.frame(domain='my domain'):
            pass

        domain_class_mock.assert_called_once_with('my domain')

    @pyitt_native_patch('Domain')
    def test_frame_creation_for_callable_object(self, domain_class_mock):
        domain_class_mock.return_value = 'domain'

        class CallableClass:
            def __call__(self, *args, **kwargs):
                pass  # pragma: no cover

        frame = pyitt.frame(CallableClass())

        self.assertEqual(frame.domain(), domain_class_mock.return_value)
        self.assertIsNone(frame.id())

    @pyitt_native_patch('Domain')
    def test_frame_creation_for_callable_object_with_deffered_call(self, domain_class_mock):
        domain_class_mock.return_value = 'domain'

        class CallableClass:
            def __call__(self, *args, **kwargs):
                pass  # pragma: no cover

        frame = pyitt.frame()
        frame(CallableClass())

        self.assertEqual(frame.domain(), domain_class_mock.return_value)
        self.assertIsNone(frame.id())

    @pyitt_native_patch('Domain')
    def test_frame_creation_for_method(self, domain_class_mock):
        class MyClass:  # pylint: disable=W0612
            @pyitt.frame
            def my_method(self):
                pass  # pragma: no cover

        domain_class_mock.assert_called_once_with(None)

    @pyitt_native_patch('Domain')
    def test_frame_creation_with_domain_object(self, domain_class_mock):
        domain = Mock()

        frame = pyitt.frame(domain=domain)

        domain_class_mock.assert_not_called()

        self.assertEqual(frame.domain(), domain)


class FramePropertiesTest(TestCase):
    @pyitt_native_patch('Domain')
    def test_frame_properties(self, domain_class_mock):
        domain_class_mock.side_effect = lambda x: x

        class CallableClass:
            def __call__(self, *args, **kwargs):
                pass  # pragma: no cover

        domain_name = 'my domain'
        frame_id = 1
        frame = pyitt.frame(CallableClass(), domain=domain_name, id=frame_id)

        self.assertEqual(frame.domain(), domain_name)
        self.assertEqual(frame.id(), frame_id)

        self.assertEqual(str(frame), f"{{ domain: '{str(domain_name)}', id: {str(frame_id)} }}")
        self.assertEqual(repr(frame), f'{frame.__class__.__name__}({repr(domain_name)}, {repr(frame_id)})')


class FrameExecutionTests(TestCase):
    @pyitt_native_patch('Domain')
    @pyitt_native_patch('frame_begin')
    @pyitt_native_patch('frame_end')
    def test_frame_for_function(self, domain_class_mock, frame_begin_mock, frame_end_mock):
        domain_class_mock.return_value = 'domain_handle'

        @pyitt.frame
        def my_function():
            return 42

        domain_class_mock.assert_called_once_with(None)

        self.assertEqual(my_function(), 42)

        frame_begin_mock.assert_called_once_with(domain_class_mock.return_value, None)
        frame_end_mock.assert_called_once_with(domain_class_mock.return_value, None)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('frame_begin')
    @pyitt_native_patch('frame_end')
    def test_nested_frames_for_function(self, domain_class_mock, frame_begin_mock, frame_end_mock):
        domain_class_mock.side_effect = lambda x: x

        @pyitt.frame
        @pyitt.frame(domain='the other domain')
        def my_function():
            return 42

        expected_calls = [call('the other domain'),
                          call(None)]
        domain_class_mock.assert_has_calls(expected_calls)

        self.assertEqual(my_function(), 42)

        expected_calls = [call(None, None),
                          call('the other domain', None)]
        frame_begin_mock.assert_has_calls(expected_calls)

        expected_calls = [call('the other domain', None),
                          call(None, None)]
        frame_end_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('frame_begin')
    @pyitt_native_patch('frame_end')
    def test_frame_as_context_manager(self, domain_class_mock, frame_begin_mock, frame_end_mock):
        domain_class_mock.return_value = 'domain_handle'

        with pyitt.frame():
            pass

        domain_class_mock.assert_called_once_with(None)

        frame_begin_mock.assert_called_once_with(domain_class_mock.return_value, None)
        frame_end_mock.assert_called_once_with(domain_class_mock.return_value, None)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('frame_begin')
    @pyitt_native_patch('frame_end')
    def test_frame_for_callable_object(self, domain_class_mock, frame_begin_mock, frame_end_mock):
        domain_class_mock.return_value = 'domain_handle'

        class CallableClass:
            def __call__(self, *args, **kwargs):
                return 42

        callable_object = pyitt.frame(CallableClass())
        domain_class_mock.assert_called_once_with(None)

        self.assertEqual(callable_object(), 42)

        frame_begin_mock.assert_called_once_with(domain_class_mock.return_value, None)
        frame_end_mock.assert_called_once_with(domain_class_mock.return_value, None)

    def test_frame_for_noncallable_object(self):
        with self.assertRaises(TypeError) as context:
            pyitt.frame()(42)

        self.assertEqual(str(context.exception), 'Callable object or method descriptor are expected to be passed.')

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('frame_begin')
    @pyitt_native_patch('frame_end')
    def test_frame_for_method(self, domain_class_mock, frame_begin_mock, frame_end_mock):
        domain_class_mock.return_value = 'domain_handle'

        class MyClass:
            @pyitt.frame
            def my_method(self):
                return 42

        domain_class_mock.assert_called_once_with(None)

        my_object = MyClass()
        self.assertEqual(my_object.my_method(), 42)

        frame_begin_mock.assert_called_once_with(domain_class_mock.return_value, None)
        frame_end_mock.assert_called_once_with(domain_class_mock.return_value, None)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('frame_begin')
    @pyitt_native_patch('frame_end')
    def test_frame_for_class_method(self, domain_class_mock, frame_begin_mock, frame_end_mock):
        domain_class_mock.return_value = 'domain_handle'

        class MyClass:
            @classmethod
            @pyitt.frame
            def my_class_method(cls):
                return 42

        domain_class_mock.assert_called_once_with(None)

        self.assertEqual(MyClass.my_class_method(), 42)

        frame_begin_mock.assert_called_once_with(domain_class_mock.return_value, None)
        frame_end_mock.assert_called_once_with(domain_class_mock.return_value, None)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('frame_begin')
    @pyitt_native_patch('frame_end')
    def test_frame_for_static_method(self, domain_class_mock, frame_begin_mock, frame_end_mock):
        domain_class_mock.return_value = 'domain_handle'

        class MyClass:
            @staticmethod
            @pyitt.frame
            def my_static_method():
                return 42

        domain_class_mock.assert_called_once_with(None)

        self.assertEqual(MyClass.my_static_method(), 42)

        frame_begin_mock.assert_called_once_with(domain_class_mock.return_value, None)
        frame_end_mock.assert_called_once_with(domain_class_mock.return_value, None)

        frame_begin_mock.reset_mock()
        frame_end_mock.reset_mock()

        self.assertEqual(MyClass().my_static_method(), 42)

        frame_begin_mock.assert_called_once_with(domain_class_mock.return_value, None)
        frame_end_mock.assert_called_once_with(domain_class_mock.return_value, None)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('frame_begin')
    @pyitt_native_patch('frame_end')
    def test_frame_for_function_raised_exception(self, domain_class_mock, frame_begin_mock, frame_end_mock):
        domain_class_mock.return_value = 'domain_handle'

        exception_msg = 'ValueError exception from my_function'

        @pyitt.frame
        def my_function():
            raise ValueError(exception_msg)

        domain_class_mock.assert_called_once_with(None)

        with self.assertRaises(ValueError) as context:
            my_function()

        self.assertEqual(str(context.exception), exception_msg)

        frame_begin_mock.assert_called_once_with(domain_class_mock.return_value, None)
        frame_end_mock.assert_called_once_with(domain_class_mock.return_value, None)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('frame_begin')
    @pyitt_native_patch('frame_end')
    def test_frame_for_method_raised_exception(self, domain_class_mock, frame_begin_mock, frame_end_mock):
        domain_class_mock.return_value = 'domain_handle'

        exception_msg = 'ValueError exception from my_method'

        class MyClass:
            @pyitt.frame
            def my_method(self):
                raise ValueError(exception_msg)

        domain_class_mock.assert_called_once_with(None)

        with self.assertRaises(ValueError) as context:
            MyClass().my_method()

        self.assertEqual(str(context.exception), exception_msg)

        frame_begin_mock.assert_called_once_with(domain_class_mock.return_value, None)
        frame_end_mock.assert_called_once_with(domain_class_mock.return_value, None)

    @pyitt_native_patch('Domain')
    @pyitt_native_patch('frame_begin')
    @pyitt_native_patch('frame_end')
    def test_overlapped_frames(self, domain_class_mock, frame_begin_mock, frame_end_mock):
        domain_class_mock.side_effect = lambda x: x

        overlapped_frame_1_domain = 'overlapped frame domain 1'
        overlapped_frame_2_domain = 'overlapped frame domain 2'

        overlapped_frame_1 = pyitt.frame(domain=overlapped_frame_1_domain)
        overlapped_frame_1.begin()

        overlapped_frame_2 = pyitt.frame(domain=overlapped_frame_2_domain)
        overlapped_frame_2.begin()

        overlapped_frame_1.end()
        overlapped_frame_2.end()

        expected_calls = [
            call(overlapped_frame_1_domain, None),
            call(overlapped_frame_2_domain, None)
        ]
        frame_begin_mock.assert_has_calls(expected_calls)
        frame_end_mock.assert_has_calls(expected_calls)


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
