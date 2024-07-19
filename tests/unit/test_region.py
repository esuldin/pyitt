from asyncio import sleep, iscoroutinefunction
from functools import partial
from inspect import stack
from os.path import basename
from unittest import main as unittest_main, TestCase, IsolatedAsyncioTestCase
from unittest.mock import call, Mock

from .pyitt_native_mock import patch as pyitt_native_patch
from pyitt.region import _CallSite, _NamedRegion, _Region  # pylint: disable=C0411


class TestRegion(_Region):
    def __init__(self, func=None) -> None:
        super().__init__(func)
        self.region = self
        self.number_of_begin_method_calls = 0
        self.number_of_end_method_calls = 0
        self.number_of_wrap_callback_method_calls = 0

        self._on_wrapping = partial(TestRegion.wrap_callback, self)

    def begin(self) -> None:
        self.number_of_begin_method_calls += 1

    def end(self) -> None:
        self.number_of_end_method_calls += 1

    def wrap_callback(self, func) -> None:  # pylint: disable=W0613
        setattr(func, 'region', self)

        self.number_of_wrap_callback_method_calls += 1


class RegionAbstractMethodsTests(TestCase):
    def test_region_abstract_method_begin(self):
        with self.assertRaises(NotImplementedError):
            _Region.begin(TestRegion())

    def test_region_abstract_method_end(self):
        with self.assertRaises(NotImplementedError):
            _Region.end(TestRegion())


class RegionCreationTests(TestCase):
    def test_region_creation_with_default_constructor(self):
        region = TestRegion()

        def my_function():
            pass  # pragma: no cover

        wrapped_function = region(my_function)
        self.assertEqual(wrapped_function.__name__, 'my_function')

    def test_region_creation_as_decorator_for_function(self):
        @TestRegion
        def my_function():
            pass  # pragma: no cover

        self.assertEqual(my_function.__name__, 'my_function')

    def test_region_creation_as_decorator_for_async_function(self):
        @TestRegion
        async def my_function():
            pass  # pragma: no cover

        self.assertEqual(my_function.__name__, 'my_function')
        self.assertTrue(iscoroutinefunction(my_function))

    def test_region_creation_as_decorator_for_generator_function(self):
        @TestRegion
        def my_function():
            yield 42  # pragma: no cover

        self.assertEqual(my_function.__name__, 'my_function')

    def test_region_creation_as_decorator_with_empty_arguments_for_function(self):
        @TestRegion()
        def my_function():
            pass  # pragma: no cover

        self.assertEqual(my_function.__name__, 'my_function')

    def test_region_creation_for_already_wrapped_function(self):
        @TestRegion
        @TestRegion()
        def my_function():
            pass  # pragma: no cover

        self.assertEqual(my_function.__name__, 'my_function')

    def test_region_creation_with_default_constructor_as_context_manager(self):
        with TestRegion() as region:
            self.assertIsNotNone(region)

    def test_region_creation_for_callable_object(self):
        class CallableClass:
            def __call__(self, *args, **kwargs):
                pass  # pragma: no cover

        callable_object = CallableClass()
        self.assertIsNotNone(TestRegion(callable_object))

    def test_region_creation_for_method(self):
        class MyClass:
            @TestRegion
            def my_method(self):
                pass  # pragma: no cover

        self.assertEqual(MyClass.my_method.__name__, 'my_method')

    def test_region_creation_for_async_method(self):
        class MyClass:
            @TestRegion
            async def my_method(self):
                await sleep(0)  # pragma: no cover

        self.assertEqual(MyClass.my_method.__name__, 'my_method')
        self.assertTrue(iscoroutinefunction(MyClass.my_method))

    def test_region_creation_for_generator_method(self):
        class MyClass:
            @TestRegion
            def my_method(self):
                yield 42  # pragma: no cover

        self.assertEqual(MyClass.my_method.__name__, 'my_method')

    def test_region_creation_for_noncallable_object(self):
        with self.assertRaises(TypeError) as context:
            TestRegion(42)

        self.assertEqual(str(context.exception), 'func must be a callable object, method descriptor or None.')

    def test_region_creation_for_class_method(self):
        class MyClass:
            @TestRegion
            @classmethod
            def my_class_method(cls):
                pass  # pragma: no cover

        self.assertTrue(hasattr(MyClass.my_class_method, '__wrapped__'))

    def test_region_creation_for_async_class_method(self):
        class MyClass:
            @TestRegion
            @classmethod
            async def my_class_method(cls):
                await sleep(0)  # pragma: no cover

        self.assertTrue(hasattr(MyClass.my_class_method, '__wrapped__'))

    def test_region_creation_for_generator_class_method(self):
        class MyClass:
            @TestRegion
            @classmethod
            def my_class_method(cls):
                yield 42  # pragma: no cover

        self.assertTrue(hasattr(MyClass.my_class_method, '__wrapped__'))

    def test_region_creation_for_static_method(self):
        class MyClass:
            @TestRegion
            @staticmethod
            def my_static_method():
                pass  # pragma: no cover

        self.assertTrue(hasattr(MyClass.my_static_method, '__wrapped__'))

    def test_region_creation_for_async_static_method(self):
        class MyClass:
            @TestRegion
            @staticmethod
            async def my_static_method():
                await sleep(0)  # pragma: no cover

        self.assertTrue(hasattr(MyClass.my_static_method, '__wrapped__'))

    def test_region_creation_for_generator_static_method(self):
        class MyClass:
            @TestRegion
            @staticmethod
            def my_static_method():
                yield 42  # pragma: no cover

        self.assertTrue(hasattr(MyClass.my_static_method, '__wrapped__'))

    def test_region_creation_as_descriptor_wo_arguments(self):
        class MyClass:
            my_method = TestRegion()

        with self.assertRaises(TypeError) as context:
            MyClass().my_method()

        self.assertEqual(str(context.exception), 'Callable object or method descriptor are expected to be passed.')


class RegionPropertiesTests(TestCase):
    def test_region_on_wrapping_callback(self):
        region = TestRegion()
        callback_mock = Mock()

        # pylint: disable=W0212
        region._on_wrapping = callback_mock
        self.assertEqual(region._on_wrapping, callback_mock)


# pylint: disable=R0904
class RegionExecutionTests(TestCase):
    def test_region_for_function(self):
        @TestRegion
        def my_function():
            return 42

        self.assertEqual(my_function(), 42)
        self.assertEqual(my_function.number_of_begin_method_calls, 1)
        self.assertEqual(my_function.number_of_end_method_calls, 1)
        self.assertEqual(my_function.number_of_wrap_callback_method_calls, 1)

    def test_region_for_generator_function(self):
        @TestRegion
        def my_function():
            yield 42

        generator = my_function()

        self.assertEqual(my_function.number_of_begin_method_calls, 0)
        self.assertEqual(my_function.number_of_end_method_calls, 0)
        self.assertEqual(my_function.number_of_wrap_callback_method_calls, 1)

        generator_iterator = iter(generator)
        self.assertEqual(next(generator_iterator), 42)

        self.assertEqual(my_function.number_of_begin_method_calls, 1)
        self.assertEqual(my_function.number_of_end_method_calls, 0)
        self.assertEqual(my_function.number_of_wrap_callback_method_calls, 1)

        with self.assertRaises(StopIteration):
            next(generator_iterator)

        self.assertEqual(my_function.number_of_begin_method_calls, 1)
        self.assertEqual(my_function.number_of_end_method_calls, 1)
        self.assertEqual(my_function.number_of_wrap_callback_method_calls, 1)

    def test_nested_regions_for_function(self):
        @TestRegion
        @TestRegion()
        def my_function():
            return 42

        self.assertEqual(my_function(), 42)
        self.assertEqual(my_function.number_of_begin_method_calls, 1)
        self.assertEqual(my_function.number_of_end_method_calls, 1)
        self.assertEqual(my_function.number_of_wrap_callback_method_calls, 1)

    def test_region_as_context_manager(self):
        with TestRegion() as region:
            self.assertTrue(isinstance(region, TestRegion))

        self.assertEqual(region.number_of_begin_method_calls, 1)
        self.assertEqual(region.number_of_end_method_calls, 1)
        self.assertEqual(region.number_of_wrap_callback_method_calls, 0)

    def test_region_for_callable_object(self):
        class CallableClass:
            def __call__(self, *args, **kwargs):
                return 42

        callable_object = CallableClass()
        wrapped_object = TestRegion(callable_object)
        self.assertEqual(wrapped_object(), 42)
        self.assertEqual(wrapped_object.number_of_begin_method_calls, 1)
        self.assertEqual(wrapped_object.number_of_end_method_calls, 1)
        self.assertEqual(wrapped_object.number_of_wrap_callback_method_calls, 1)

    def test_region_multiple_calls(self):
        class CallableClass:
            def __call__(self, *args, **kwargs):
                return 42

        region = TestRegion()

        callable_object = CallableClass()
        wrapped_object = region(callable_object)
        self.assertEqual(wrapped_object, region)
        self.assertEqual(wrapped_object(), 42)

    def test_region_for_noncallable_object(self):
        with self.assertRaises(TypeError) as context:
            TestRegion()(42)

        self.assertEqual(str(context.exception), 'Callable object or method descriptor are expected to be passed.')

    def test_region_for_method(self):
        class MyClass:
            @TestRegion
            def my_method(self):
                return 42

        my_object = MyClass()
        self.assertEqual(my_object.my_method(), 42)
        # pylint: disable=E1101
        self.assertEqual(MyClass.my_method.region.number_of_begin_method_calls, 1)
        self.assertEqual(MyClass.my_method.region.number_of_end_method_calls, 1)
        self.assertEqual(MyClass.my_method.region.number_of_wrap_callback_method_calls, 1)

    def test_region_for_generator_method(self):
        class MyClass:
            @TestRegion
            def my_method(self):
                yield 42

        my_object = MyClass()
        generator_iterator = iter(my_object.my_method())
        self.assertEqual(next(generator_iterator), 42)
        # pylint: disable=E1101
        self.assertEqual(MyClass.my_method.region.number_of_begin_method_calls, 1)
        self.assertEqual(MyClass.my_method.region.number_of_end_method_calls, 0)
        self.assertEqual(MyClass.my_method.region.number_of_wrap_callback_method_calls, 1)

        with self.assertRaises(StopIteration):
            next(generator_iterator)
        self.assertEqual(MyClass.my_method.region.number_of_begin_method_calls, 1)
        self.assertEqual(MyClass.my_method.region.number_of_end_method_calls, 1)
        self.assertEqual(MyClass.my_method.region.number_of_wrap_callback_method_calls, 1)

    def test_region_for_method_when_it_is_called_using_classinfo(self):
        # pylint: disable=E1120
        class MyClass:
            @TestRegion
            def my_method(self):
                return 42

        self.assertEqual(MyClass.my_method(None), 42)

    def test_region_for_method_with_dynamic_replacing_method_in_classinfo(self):
        class MyClass:
            def my_method(self):
                return 42

        MyClass.my_method = TestRegion()(MyClass.my_method)

        my_object = MyClass()

        self.assertEqual(my_object.my_method(), 42)
        # pylint: disable=E1101
        self.assertEqual(MyClass.my_method.region.number_of_begin_method_calls, 1)
        self.assertEqual(MyClass.my_method.region.number_of_end_method_calls, 1)
        self.assertEqual(MyClass.my_method.region.number_of_wrap_callback_method_calls, 1)

    def test_region_for_method_with_dynamic_replacing_method_in_object(self):
        class MyClass:
            def my_method(self):
                return 42

        my_object = MyClass()
        my_object.my_method = TestRegion()(partial(MyClass.my_method, my_object))

        self.assertEqual(my_object.my_method(), 42)
        self.assertEqual(my_object.my_method.number_of_begin_method_calls, 1)
        self.assertEqual(my_object.my_method.number_of_end_method_calls, 1)
        self.assertEqual(my_object.my_method.number_of_wrap_callback_method_calls, 1)

    def test_region_for_class_method(self):
        class MyClass:
            @classmethod
            @TestRegion
            def my_class_method(cls):
                return 42

        self.assertEqual(MyClass.my_class_method(), 42)
        self.assertEqual(MyClass.my_class_method.region.number_of_begin_method_calls, 1)
        self.assertEqual(MyClass.my_class_method.region.number_of_end_method_calls, 1)
        self.assertEqual(MyClass.my_class_method.region.number_of_wrap_callback_method_calls, 1)

    def test_region_for_static_method(self):
        class MyClass:
            @staticmethod
            @TestRegion
            def my_static_method():
                return 42

        self.assertEqual(MyClass.my_static_method(), 42)
        self.assertEqual(MyClass.my_static_method.number_of_begin_method_calls, 1)
        self.assertEqual(MyClass.my_static_method.number_of_end_method_calls, 1)
        self.assertEqual(MyClass.my_static_method.number_of_wrap_callback_method_calls, 1)

        self.assertEqual(MyClass().my_static_method(), 42)
        self.assertEqual(MyClass.my_static_method.number_of_begin_method_calls, 2)
        self.assertEqual(MyClass.my_static_method.number_of_end_method_calls, 2)
        self.assertEqual(MyClass.my_static_method.number_of_wrap_callback_method_calls, 1)

    def test_region_on_top_of_staticmethod_decorator(self):
        class MyClass:
            @TestRegion
            @staticmethod
            def my_static_method():
                return 42

        self.assertEqual(MyClass.my_static_method(), 42)
        self.assertEqual(MyClass.my_static_method.region.number_of_begin_method_calls, 1)
        self.assertEqual(MyClass.my_static_method.region.number_of_end_method_calls, 1)
        self.assertEqual(MyClass.my_static_method.region.number_of_wrap_callback_method_calls, 1)

        self.assertEqual(MyClass().my_static_method(), 42)
        self.assertEqual(MyClass.my_static_method.region.number_of_begin_method_calls, 2)
        self.assertEqual(MyClass.my_static_method.region.number_of_end_method_calls, 2)
        self.assertEqual(MyClass.my_static_method.region.number_of_wrap_callback_method_calls, 1)

    def test_region_on_top_of_staticmethod_decorator_for_generator(self):
        class MyClass:
            @TestRegion
            @staticmethod
            def my_static_method():
                yield 42

        generator_iterator = iter(MyClass.my_static_method())

        self.assertEqual(next(generator_iterator), 42)
        self.assertEqual(MyClass.my_static_method.region.number_of_begin_method_calls, 1)
        self.assertEqual(MyClass.my_static_method.region.number_of_end_method_calls, 0)
        self.assertEqual(MyClass.my_static_method.region.number_of_wrap_callback_method_calls, 1)

        with self.assertRaises(StopIteration):
            next(generator_iterator)
        self.assertEqual(MyClass.my_static_method.region.number_of_begin_method_calls, 1)
        self.assertEqual(MyClass.my_static_method.region.number_of_end_method_calls, 1)
        self.assertEqual(MyClass.my_static_method.region.number_of_wrap_callback_method_calls, 1)

    def test_region_on_top_of_classmethod_decorator(self):
        class MyClass:
            @TestRegion
            @classmethod
            def my_class_method(cls):
                return 42

        self.assertEqual(MyClass.my_class_method(), 42)
        self.assertEqual(MyClass.my_class_method.region.number_of_begin_method_calls, 1)
        self.assertEqual(MyClass.my_class_method.region.number_of_end_method_calls, 1)
        self.assertEqual(MyClass.my_class_method.region.number_of_wrap_callback_method_calls, 1)

        self.assertEqual(MyClass().my_class_method(), 42)
        self.assertEqual(MyClass.my_class_method.region.number_of_begin_method_calls, 2)
        self.assertEqual(MyClass.my_class_method.region.number_of_end_method_calls, 2)
        self.assertEqual(MyClass.my_class_method.region.number_of_wrap_callback_method_calls, 1)

    def test_region_on_top_of_classmethod_decorator_for_generator(self):
        class MyClass:
            @TestRegion
            @classmethod
            def my_class_method(cls):
                yield 42

        generator_iterator = iter(MyClass.my_class_method())

        self.assertEqual(next(generator_iterator), 42)
        self.assertEqual(MyClass.my_class_method.region.number_of_begin_method_calls, 1)
        self.assertEqual(MyClass.my_class_method.region.number_of_end_method_calls, 0)
        self.assertEqual(MyClass.my_class_method.region.number_of_wrap_callback_method_calls, 1)

        with self.assertRaises(StopIteration):
            next(generator_iterator)
        self.assertEqual(MyClass.my_class_method.region.number_of_begin_method_calls, 1)
        self.assertEqual(MyClass.my_class_method.region.number_of_end_method_calls, 1)
        self.assertEqual(MyClass.my_class_method.region.number_of_wrap_callback_method_calls, 1)

    def test_region_for_function_raised_exception(self):
        exception_msg = 'ValueError exception from my_function'

        @TestRegion
        def my_function():
            raise ValueError(exception_msg)

        with self.assertRaises(ValueError) as context:
            my_function()

        self.assertEqual(str(context.exception), exception_msg)

        self.assertEqual(my_function.number_of_begin_method_calls, 1)
        self.assertEqual(my_function.number_of_end_method_calls, 1)
        self.assertEqual(my_function.number_of_wrap_callback_method_calls, 1)

    def test_region_for_method_raised_exception(self):
        exception_msg = 'ValueError exception from my_method'

        class MyClass:
            @TestRegion
            def my_method(self):
                raise ValueError(exception_msg)

        with self.assertRaises(ValueError) as context:
            MyClass().my_method()

        self.assertEqual(str(context.exception), exception_msg)
        # pylint: disable=E1101
        self.assertEqual(MyClass.my_method.region.number_of_begin_method_calls, 1)
        self.assertEqual(MyClass.my_method.region.number_of_end_method_calls, 1)
        self.assertEqual(MyClass.my_method.region.number_of_wrap_callback_method_calls, 1)

    def test_region_for_closing_generator(self):
        @TestRegion
        def my_function():
            yield 42

        generator = my_function()

        self.assertEqual(my_function.number_of_begin_method_calls, 0)
        self.assertEqual(my_function.number_of_end_method_calls, 0)
        self.assertEqual(my_function.number_of_wrap_callback_method_calls, 1)

        generator_iterator = iter(generator)
        self.assertEqual(next(generator_iterator), 42)

        self.assertEqual(my_function.number_of_begin_method_calls, 1)
        self.assertEqual(my_function.number_of_end_method_calls, 0)
        self.assertEqual(my_function.number_of_wrap_callback_method_calls, 1)

        generator.close()
        self.assertEqual(my_function.number_of_begin_method_calls, 1)
        self.assertEqual(my_function.number_of_end_method_calls, 1)
        self.assertEqual(my_function.number_of_wrap_callback_method_calls, 1)

    def test_region_for_throwing_exception_in_generator(self):
        @TestRegion
        def my_function():
            yield 42

        generator = my_function()

        self.assertEqual(my_function.number_of_begin_method_calls, 0)
        self.assertEqual(my_function.number_of_end_method_calls, 0)
        self.assertEqual(my_function.number_of_wrap_callback_method_calls, 1)

        generator_iterator = iter(generator)
        self.assertEqual(next(generator_iterator), 42)

        self.assertEqual(my_function.number_of_begin_method_calls, 1)
        self.assertEqual(my_function.number_of_end_method_calls, 0)
        self.assertEqual(my_function.number_of_wrap_callback_method_calls, 1)

        with self.assertRaises(GeneratorExit):
            generator.throw(GeneratorExit)
        self.assertEqual(my_function.number_of_begin_method_calls, 1)
        self.assertEqual(my_function.number_of_end_method_calls, 1)
        self.assertEqual(my_function.number_of_wrap_callback_method_calls, 1)


class AsyncRegionExecutionTest(IsolatedAsyncioTestCase):
    async def test_region_for_async_function(self):
        @TestRegion
        async def my_function():
            return await sleep(0.01, result=42)

        self.assertEqual(await my_function(), 42)
        self.assertEqual(my_function.number_of_begin_method_calls, 1)
        self.assertEqual(my_function.number_of_end_method_calls, 1)
        self.assertEqual(my_function.number_of_wrap_callback_method_calls, 1)

    async def test_region_for_async_method(self):
        class MyClass:
            @TestRegion
            async def my_method(self):
                return await sleep(0.01, result=42)

        self.assertEqual(await MyClass().my_method(), 42)
        # pylint: disable=E1101
        self.assertEqual(MyClass.my_method.region.number_of_begin_method_calls, 1)
        self.assertEqual(MyClass.my_method.region.number_of_end_method_calls, 1)
        self.assertEqual(MyClass.my_method.region.number_of_wrap_callback_method_calls, 1)

    async def test_region_for_async_class_method(self):
        class MyClass:
            @TestRegion
            @classmethod
            async def my_method(cls):
                return await sleep(0.01, result=42)

        self.assertEqual(await MyClass.my_method(), 42)
        self.assertEqual(MyClass.my_method.region.number_of_begin_method_calls, 1)
        self.assertEqual(MyClass.my_method.region.number_of_end_method_calls, 1)
        self.assertEqual(MyClass.my_method.region.number_of_wrap_callback_method_calls, 1)


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
