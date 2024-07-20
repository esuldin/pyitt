from asyncio import sleep
from inspect import stack
from os.path import basename
from unittest import main as unittest_main, TestCase
from unittest.mock import call, Mock

from .pyitt_native_mock import patch as pyitt_native_patch
from pyitt._named_region import _CallSite, _NamedRegion  # pylint: disable=C0411


class CallSiteTest(TestCase):
    def test_call_site_creation(self):
        caller = stack()[0]
        call_site = _CallSite(_CallSite.CallerFrame-1)

        self.assertEqual(call_site.filename, basename(caller.filename))
        self.assertEqual(call_site.lineno, caller.lineno+1)


class TestNamedRegion(_NamedRegion):
    def begin(self) -> None:
        pass

    def end(self) -> None:
        pass


class NamedRegionAbstractMethodsTests(TestCase):
    def test_region_abstract_method_begin(self):
        with self.assertRaises(NotImplementedError):
            _NamedRegion.begin(TestNamedRegion())

    def test_region_abstract_method_end(self):
        with self.assertRaises(NotImplementedError):
            _NamedRegion.end(TestNamedRegion())


class NamedRegionCreationTests(TestCase):
    @pyitt_native_patch('StringHandle')
    def test_region_creation_with_default_constructor(self, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        region = TestNamedRegion()
        self.assertEqual(region.name, None)

        string_handle_class_mock.assert_not_called()

    @pyitt_native_patch('StringHandle')
    def test_region_creation_as_decorator_for_function(self, string_handle_class_mock):
        @TestNamedRegion
        def my_function():
            pass  # pragma: no cover

        string_handle_class_mock.assert_called_once_with(my_function.__qualname__)

    @pyitt_native_patch('StringHandle')
    def test_region_creation_as_decorator_with_empty_arguments_for_function(self, string_handle_class_mock):
        @TestNamedRegion()
        def my_function():
            pass  # pragma: no cover

        string_handle_class_mock.assert_called_with(my_function.__qualname__)

    @pyitt_native_patch('StringHandle')
    def test_region_creation_as_decorator_with_name_for_function(self, string_handle_class_mock):
        @TestNamedRegion('my function')
        def my_function():
            pass  # pragma: no cover

        string_handle_class_mock.assert_called_once_with('my function')

    @pyitt_native_patch('StringHandle')
    def test_region_creation_as_decorator_with_empty_args_and_name_for_function(self, string_handle_class_mock):
        @TestNamedRegion
        @TestNamedRegion('my function')
        def my_function():
            pass  # pragma: no cover

        expected_calls = [call('my function'),
                          call(my_function.__qualname__)]
        string_handle_class_mock.assert_has_calls(expected_calls)

    @pyitt_native_patch('StringHandle')
    def test_region_creation_with_default_constructor_as_context_manager(self, string_handle_class_mock):
        with TestNamedRegion():
            pass

        string_handle_class_mock.assert_not_called()

    @pyitt_native_patch('StringHandle')
    def test_region_creation_with_name_and_domain_as_context_manager(self, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        task_name = 'my task'
        with TestNamedRegion(task_name) as task:
            self.assertEqual(task.name, task_name)

        string_handle_class_mock.assert_called_once_with('my task')

    @pyitt_native_patch('StringHandle')
    def test_region_creation_for_callable_object(self, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        class CallableClass:
            def __call__(self, *args, **kwargs):
                pass  # pragma: no cover

        region = TestNamedRegion(CallableClass())

        expected_name = f'{CallableClass.__qualname__}.__call__'
        string_handle_class_mock.assert_called_once_with(expected_name)

        self.assertEqual(region.name, expected_name)

    @pyitt_native_patch('StringHandle')
    def test_unnamed_region_creation_for_callable_object(self, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        class CallableClass:
            def __call__(self, *args, **kwargs):
                pass  # pragma: no cover

        region = TestNamedRegion()
        region(CallableClass())

        expected_name = f'{CallableClass.__qualname__}.__call__'
        expected_calls = [
            call(expected_name)
        ]
        string_handle_class_mock.assert_has_calls(expected_calls)

        self.assertEqual(region.name, expected_name)

    @pyitt_native_patch('StringHandle')
    def test_region_creation_for_method(self, string_handle_class_mock):
        class MyClass:
            @TestNamedRegion
            def my_method(self):
                pass  # pragma: no cover

        string_handle_class_mock.assert_called_once_with(f'{MyClass.my_method.__qualname__}')

    @pyitt_native_patch('StringHandle')
    def test_region_creation_for_async_method(self, string_handle_class_mock):
        class MyClass:
            @TestNamedRegion
            async def my_method(self):
                await sleep(0)  # pragma: no cover

        string_handle_class_mock.assert_called_once_with(f'{MyClass.my_method.__qualname__}')

    @pyitt_native_patch('StringHandle')
    def test_region_creation_for_class_method(self, string_handle_class_mock):
        class MyClass:
            @TestNamedRegion
            @classmethod
            def my_class_method(cls):
                pass  # pragma: no cover

        string_handle_class_mock.assert_called_once_with(
            f'{MyClass.my_class_method.__wrapped__.__class__.__qualname__}.__call__')

    @pyitt_native_patch('StringHandle')
    def test_region_creation_for_async_class_method(self, string_handle_class_mock):
        class MyClass:
            @TestNamedRegion
            @classmethod
            async def my_class_method(cls):
                await sleep(0)  # pragma: no cover

        string_handle_class_mock.assert_called_once_with(
            f'{MyClass.my_class_method.__wrapped__.__class__.__qualname__}.__call__')

    @pyitt_native_patch('StringHandle')
    def test_region_creation_for_static_method(self, string_handle_class_mock):
        class MyClass:
            @TestNamedRegion
            @staticmethod
            def my_static_method():
                pass  # pragma: no cover

        string_handle_class_mock.assert_called_once_with(
            f'{MyClass.my_static_method.__wrapped__.__class__.__qualname__}.__call__')

    @pyitt_native_patch('StringHandle')
    def test_region_creation_for_async_static_method(self, string_handle_class_mock):
        class MyClass:
            @TestNamedRegion
            @staticmethod
            async def my_static_method():
                await sleep(0)  # pragma: no cover

        string_handle_class_mock.assert_called_once_with(
            f'{MyClass.my_static_method.__wrapped__.__class__.__qualname__}.__call__')

    @pyitt_native_patch('StringHandle')
    def test_region_creation_as_descriptor(self, string_handle_class_mock):
        class MyClass:
            my_method = TestNamedRegion()

        string_handle_class_mock.assert_called_once_with(f'{MyClass.__qualname__}.my_method')

    @pyitt_native_patch('StringHandle')
    def test_region_creation_for_callable_object_with_name_attribute(self, string_handle_class_mock):
        class MyClass:
            def __call__(self):
                pass  # pragma: no cover

        my_object = MyClass()
        my_object_name = 'my_object'
        setattr(my_object, '__name__', my_object_name)

        TestNamedRegion(my_object)

        string_handle_class_mock.assert_called_with(my_object_name)

    @pyitt_native_patch('StringHandle')
    def test_region_creation_for_callsite(self, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        callsite = _CallSite(_CallSite.CallerFrame-1)
        TestNamedRegion(callsite)

        string_handle_class_mock.assert_called_with(f'{callsite.filename}:{callsite.lineno}')


class NamedRegionPropertiesTest(TestCase):
    @pyitt_native_patch('StringHandle')
    def test_region_properties(self, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        class CallableClass:
            def __call__(self, *args, **kwargs):
                pass  # pragma: no cover

        region = TestNamedRegion(CallableClass())

        expected_name = f'{CallableClass.__qualname__}.__call__'
        string_handle_class_mock.assert_called_once_with(expected_name)

        self.assertEqual(region.name, expected_name)
        self.assertEqual(str(region), expected_name)
        self.assertEqual(repr(region), f'{region.__class__.__qualname__}({repr(expected_name)})')

    @pyitt_native_patch('StringHandle')
    def test_region_on_name_determination_callback_set(self, string_handle_class_mock):
        callback_mock = Mock()
        region = TestNamedRegion()

        # pylint: disable=W0201,W0212
        region._on_name_determination = callback_mock
        self.assertEqual(region._on_name_determination, callback_mock)

        string_handle_class_mock.assert_not_called()

    @pyitt_native_patch('StringHandle')
    def test_region_on_name_determination_callback_call(self, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        def my_function():
            pass  # pragma: no cover

        callback_mock = Mock()
        region = TestNamedRegion(my_function)

        region._on_name_determination = callback_mock  # pylint: disable=W0201,W0212

        callback_mock.assert_called_once_with(my_function.__qualname__)
        string_handle_class_mock.assert_called_once_with(my_function.__qualname__)


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
