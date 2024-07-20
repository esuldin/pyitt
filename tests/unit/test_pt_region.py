from inspect import stack
from os.path import basename
from unittest import main as unittest_main, TestCase
from unittest.mock import call

from .pyitt_native_mock import patch as pyitt_native_patch
import pyitt  # pylint: disable=C0411


class PTRegionCreationTests(TestCase):
    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_creation_with_default_constructor(self, pt_region_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        region = pyitt.pt_region()
        caller = stack()[0]
        expected_name = f'{basename(caller.filename)}:{caller.lineno-1}'

        pt_region_class_mock.assert_not_called()

        region.begin()

        pt_region_class_mock.assert_called_once_with(expected_name)
        self.assertEqual(region.name, expected_name)

    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_creation_as_decorator_for_function(self, pt_region_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        @pyitt.pt_region
        def my_function():
            pass  # pragma: no cover

        pt_region_class_mock.assert_called_once_with(my_function.__qualname__)

    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_creation_as_decorator_with_empty_arguments_for_function(self, pt_region_class_mock,
                                                                               string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        @pyitt.pt_region()
        def my_function():
            pass  # pragma: no cover

        pt_region_class_mock.assert_called_with(my_function.__qualname__)

    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_creation_as_decorator_with_name_for_function(self, pt_region_class_mock,
                                                                    string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        @pyitt.pt_region('my function')
        def my_function():
            pass  # pragma: no cover

        pt_region_class_mock.assert_called_once_with('my function')

    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_creation_as_decorator_with_empty_args_and_name_for_function(self, pt_region_class_mock,
                                                                                   string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        @pyitt.pt_region
        @pyitt.pt_region('my function')
        def my_function():
            pass  # pragma: no cover

        expected_calls = [call('my function'),
                          call(my_function.__qualname__)]
        pt_region_class_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_creation_with_default_constructor_as_context_manager(self, pt_region_class_mock,
                                                                            string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        caller = stack()[0]
        with pyitt.pt_region():
            pass

        pt_region_class_mock.assert_called_once_with(f'{basename(caller.filename)}:{caller.lineno+1}')

    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_creation_with_name_and_domain_as_context_manager(self, pt_region_class_mock,
                                                                        string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x
        name = 'my pt region'

        with pyitt.pt_region(name):
            pass

        pt_region_class_mock.assert_called_once_with(name)

    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_creation_for_callable_object(self, pt_region_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        class CallableClass:
            def __call__(self, *args, **kwargs):
                pass  # pragma: no cover

        region = pyitt.pt_region(CallableClass())

        expected_name = f'{CallableClass.__qualname__}.__call__'
        pt_region_class_mock.assert_called_once_with(expected_name)

        self.assertEqual(region.name, expected_name)

    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_unnamed_pt_region_creation_for_callable_object(self, pt_region_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        class CallableClass:
            def __call__(self, *args, **kwargs):
                pass  # pragma: no cover

        region = pyitt.pt_region()
        region(CallableClass())

        expected_name = f'{CallableClass.__qualname__}.__call__'
        pt_region_class_mock.assert_called_once_with(expected_name)
        self.assertEqual(region.name, expected_name)

    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_creation_for_method(self, pt_region_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        class MyClass:
            @pyitt.pt_region
            def my_method(self):
                pass  # pragma: no cover

        pt_region_class_mock.assert_called_once_with(f'{MyClass.my_method.__qualname__}')


class PTRegionPropertiesTest(TestCase):
    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_properties(self, pt_region_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        class CallableClass:
            def __call__(self, *args, **kwargs):
                pass  # pragma: no cover

        region = pyitt.pt_region(CallableClass())

        expected_name = f'{CallableClass.__qualname__}.__call__'
        pt_region_class_mock.assert_called_once_with(expected_name)

        self.assertEqual(region.name, expected_name)

        self.assertEqual(str(region), expected_name)
        self.assertEqual(repr(region), f'{region.__class__.__name__}(\'{expected_name}\')')


class PTRegionExecutionTests(TestCase):
    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_for_function(self, pt_region_class_mock, string_handle_class_mock):
        string_handle_class_mock.return_value = 'string_handle'

        @pyitt.pt_region
        def my_function():
            return 42

        string_handle_class_mock.assert_called_once_with(my_function.__qualname__)
        pt_region_class_mock.assert_called_once_with(string_handle_class_mock.return_value)

        self.assertEqual(my_function(), 42)

        expected_calls = [call().begin(),
                          call().end()]
        pt_region_class_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_nested_regions_for_function(self, pt_region_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        @pyitt.pt_region
        @pyitt.pt_region('my function')
        def my_function():
            return 42

        expected_calls = [call('my function'),
                          call(my_function.__qualname__)]
        string_handle_class_mock.assert_has_calls(expected_calls)
        pt_region_class_mock.assert_has_calls(expected_calls)

        self.assertEqual(my_function(), 42)

        expected_calls = [call().begin(),
                          call().begin(),
                          call().end(),
                          call().end()]
        pt_region_class_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_as_context_manager(self, pt_region_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        region_name = 'my region'
        with pyitt.pt_region(region_name):
            pass

        string_handle_class_mock.assert_called_once_with(region_name)
        pt_region_class_mock.assert_called_once_with(region_name)

        expected_calls = [call().begin(),
                          call().end()]
        pt_region_class_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_for_callable_object(self, pt_region_class_mock, string_handle_class_mock):
        string_handle_class_mock.return_value = 'string_handle'

        class CallableClass:
            def __call__(self, *args, **kwargs):
                return 42

        callable_object = pyitt.pt_region(CallableClass())
        string_handle_class_mock.assert_called_once_with(f'{CallableClass.__qualname__}.__call__')
        pt_region_class_mock.assert_called_once_with(string_handle_class_mock.return_value)

        self.assertEqual(callable_object(), 42)

        expected_calls = [call().begin(),
                          call().end()]
        pt_region_class_mock.assert_has_calls(expected_calls)

    def test_pt_region_for_multiple_callable_objects(self):
        class CallableClass:
            def __call__(self, *args, **kwargs):
                return 42

        region = pyitt.pt_region()
        wrapped_object = region(CallableClass())

        self.assertEqual(wrapped_object, region)
        self.assertEqual(region(), 42)

    def test_pt_region_for_noncallable_object(self):
        with self.assertRaises(TypeError) as context:
            pyitt.pt_region()(42)

        self.assertEqual(str(context.exception), 'Callable object or method descriptor are expected to be passed.')

    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_for_method(self, pt_region_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        class MyClass:
            @pyitt.pt_region
            def my_method(self):
                return 42

        string_handle_class_mock.assert_called_once_with(f'{MyClass.my_method.__qualname__}')
        pt_region_class_mock.assert_called_once_with(f'{MyClass.my_method.__qualname__}')

        my_object = MyClass()
        self.assertEqual(my_object.my_method(), 42)

        expected_calls = [call().begin(),
                          call().end()]
        pt_region_class_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_for_class_method(self, pt_region_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        class MyClass:
            @classmethod
            @pyitt.pt_region
            def my_class_method(cls):
                return 42

        string_handle_class_mock.assert_called_once_with(f'{MyClass.my_class_method.__qualname__}')
        pt_region_class_mock.assert_called_once_with(f'{MyClass.my_class_method.__qualname__}')

        self.assertEqual(MyClass.my_class_method(), 42)

        expected_calls = [call().begin(),
                          call().end()]
        pt_region_class_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_for_static_method(self, pt_region_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        class MyClass:
            @staticmethod
            @pyitt.pt_region
            def my_static_method():
                return 42

        string_handle_class_mock.assert_called_once_with(f'{MyClass.my_static_method.__qualname__}')
        pt_region_class_mock.assert_called_once_with(f'{MyClass.my_static_method.__qualname__}')

        self.assertEqual(MyClass.my_static_method(), 42)
        self.assertEqual(MyClass().my_static_method(), 42)

        expected_calls = [call().begin(),
                          call().end(),
                          call().begin(),
                          call().end()]
        pt_region_class_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_for_function_raised_exception(self, pt_region_class_mock, string_handle_class_mock):
        string_handle_class_mock.return_value = 'string_handle'

        exception_msg = 'ValueError exception from my_function'

        @pyitt.pt_region
        def my_function():
            raise ValueError(exception_msg)

        string_handle_class_mock.assert_called_once_with(my_function.__qualname__)
        pt_region_class_mock.assert_called_once_with(string_handle_class_mock.return_value)

        with self.assertRaises(ValueError) as context:
            my_function()

        self.assertEqual(str(context.exception), exception_msg)

        expected_calls = [call().begin(),
                          call().end()]
        pt_region_class_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_for_method_raised_exception(self, pt_region_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        exception_msg = 'ValueError exception from my_method'

        class MyClass:
            @pyitt.pt_region
            def my_method(self):
                raise ValueError(exception_msg)

        string_handle_class_mock.assert_called_once_with(f'{MyClass.my_method.__qualname__}')
        pt_region_class_mock.assert_called_once_with(f'{MyClass.my_method.__qualname__}')

        with self.assertRaises(ValueError) as context:
            MyClass().my_method()

        self.assertEqual(str(context.exception), exception_msg)

        expected_calls = [call().begin(),
                          call().end()]
        pt_region_class_mock.assert_has_calls(expected_calls)


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
