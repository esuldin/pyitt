from asyncio import sleep, iscoroutinefunction
from functools import partial
from unittest import main as unittest_main, TestCase, IsolatedAsyncioTestCase
from unittest.mock import call, Mock

from pyitt._region import _AwaitableObjectWrapper, _GeneratorObjectWrapper  # pylint: disable=C0411
from pyitt._region import _Region  # pylint: disable=C0411


class AwaitableObjectWrapperTests(TestCase):
    def test_coroutine_wrapper_close_call(self):
        close_result = 42

        coroutine_close_func_mock = Mock()
        coroutine_close_func_mock.side_effect = lambda: close_result

        coroutine_obj_mock = Mock()
        coroutine_obj_mock.attach_mock(coroutine_close_func_mock, 'close')

        send_result = 42

        coroutine_send_func_mock = Mock()
        coroutine_send_func_mock.side_effect = lambda x: send_result

        coroutine_obj_mock.attach_mock(coroutine_send_func_mock, 'send')

        begin_func_mock = Mock()
        end_func_mock = Mock()

        coroutine_wrapper = _AwaitableObjectWrapper(coroutine_obj_mock, begin_func_mock, end_func_mock)
        self.assertEqual(coroutine_wrapper.send(None), send_result)
        self.assertEqual(coroutine_wrapper.close(), close_result)

        coroutine_close_func_mock.assert_called_once()
        coroutine_send_func_mock.assert_called_once_with(None)

        begin_func_mock.assert_called_once()
        end_func_mock.assert_called_once()

    def test_coroutine_wrapper_close_call_without_starting_generator(self):
        close_result = 42

        coroutine_close_func_mock = Mock()
        coroutine_close_func_mock.side_effect = lambda: close_result

        coroutine_obj_mock = Mock()
        coroutine_obj_mock.attach_mock(coroutine_close_func_mock, 'close')

        begin_func_mock = Mock()
        end_func_mock = Mock()

        coroutine_wrapper = _AwaitableObjectWrapper(coroutine_obj_mock, begin_func_mock, end_func_mock)

        self.assertEqual(coroutine_wrapper.close(), close_result)
        coroutine_close_func_mock.assert_called_once()

        begin_func_mock.assert_not_called()
        end_func_mock.assert_not_called()

    def test_coroutine_wrapper_send_call(self):
        send_result = 42

        coroutine_send_func_mock = Mock()
        coroutine_send_func_mock.side_effect = lambda x: send_result

        coroutine_obj_mock = Mock()
        coroutine_obj_mock.attach_mock(coroutine_send_func_mock, 'send')

        begin_func_mock = Mock()
        end_func_mock = Mock()

        coroutine_wrapper = _AwaitableObjectWrapper(coroutine_obj_mock, begin_func_mock, end_func_mock)
        self.assertEqual(coroutine_wrapper.send(None), send_result)
        coroutine_send_func_mock.assert_called_once_with(None)

        self.assertEqual(coroutine_wrapper.send(None), send_result)
        expected_calls = [
            call(None),
            call(None)
        ]
        coroutine_send_func_mock.assert_has_calls(expected_calls)

        begin_func_mock.assert_called_once()
        end_func_mock.assert_not_called()

    def test_coroutine_wrapper_send_call_raised_exception(self):
        exception_type = RuntimeError

        def raise_runtime_exception():
            raise exception_type()

        coroutine_send_func_mock = Mock()
        coroutine_send_func_mock.side_effect = lambda x: raise_runtime_exception()

        coroutine_obj_mock = Mock()
        coroutine_obj_mock.attach_mock(coroutine_send_func_mock, 'send')

        begin_func_mock = Mock()
        end_func_mock = Mock()

        coroutine_wrapper = _AwaitableObjectWrapper(coroutine_obj_mock, begin_func_mock, end_func_mock)

        with self.assertRaises(exception_type):
            coroutine_wrapper.send(None)

        coroutine_send_func_mock.assert_called_once_with(None)

        begin_func_mock.assert_called_once()
        end_func_mock.assert_called_once()

    def test_coroutine_wrapper_iter_call_propagation_to_send(self):
        send_result = 42

        coroutine_send_func_mock = Mock()
        coroutine_send_func_mock.side_effect = lambda x: send_result

        coroutine_obj_mock = Mock()
        coroutine_obj_mock.attach_mock(coroutine_send_func_mock, 'send')

        begin_func_mock = Mock()
        end_func_mock = Mock()

        coroutine_wrapper = _AwaitableObjectWrapper(coroutine_obj_mock, begin_func_mock, end_func_mock)
        coroutine_iterator = coroutine_wrapper.__await__()
        self.assertEqual(next(coroutine_iterator), send_result)

        coroutine_send_func_mock.assert_called_once_with(None)

        self.assertEqual(next(coroutine_iterator), send_result)

        expected_calls = [
            call(None),
            call(None)
        ]
        coroutine_send_func_mock.assert_has_calls(expected_calls)

        begin_func_mock.assert_called_once()
        end_func_mock.assert_not_called()

    def test_coroutine_wrapper_throw_call_with_handled_exception(self):
        exception_type = RuntimeError
        throw_result = 42

        coroutine_throw_func_mock = Mock()
        coroutine_throw_func_mock.side_effect = lambda x: throw_result

        coroutine_obj_mock = Mock()
        coroutine_obj_mock.attach_mock(coroutine_throw_func_mock, 'throw')

        begin_func_mock = Mock()
        end_func_mock = Mock()

        coroutine_wrapper = _AwaitableObjectWrapper(coroutine_obj_mock, begin_func_mock, end_func_mock)

        self.assertEqual(coroutine_wrapper.throw(exception_type), throw_result)

        coroutine_throw_func_mock.assert_called_once_with(exception_type)

        begin_func_mock.assert_called_once()
        end_func_mock.assert_not_called()

    def test_coroutine_wrapper_throw_call_with_unhandled_exception(self):
        exception_type = RuntimeError

        def raise_exception(ex_type):
            raise ex_type()

        coroutine_throw_func_mock = Mock()
        coroutine_throw_func_mock.side_effect = raise_exception

        coroutine_obj_mock = Mock()
        coroutine_obj_mock.attach_mock(coroutine_throw_func_mock, 'throw')

        begin_func_mock = Mock()
        end_func_mock = Mock()

        coroutine_wrapper = _AwaitableObjectWrapper(coroutine_obj_mock, begin_func_mock, end_func_mock)

        with self.assertRaises(exception_type):
            coroutine_wrapper.throw(exception_type)

        coroutine_throw_func_mock.assert_called_once_with(exception_type)

        begin_func_mock.assert_called_once()
        end_func_mock.assert_called_once()


class GeneratorObjectWrapperTests(TestCase):
    def test_generator_wrapper_close_call(self):
        close_result = 42

        generator_close_func_mock = Mock()
        generator_close_func_mock.side_effect = lambda: close_result

        generator_obj_mock = Mock()
        generator_obj_mock.attach_mock(generator_close_func_mock, 'close')

        send_result = 42

        generator_send_func_mock = Mock()
        generator_send_func_mock.side_effect = lambda x: send_result

        generator_obj_mock.attach_mock(generator_send_func_mock, 'send')

        begin_func_mock = Mock()
        end_func_mock = Mock()

        generator_wrapper = _GeneratorObjectWrapper(generator_obj_mock, begin_func_mock, end_func_mock)
        self.assertEqual(generator_wrapper.send(None), send_result)
        self.assertEqual(generator_wrapper.close(), close_result)

        generator_close_func_mock.assert_called_once()
        generator_send_func_mock.assert_called_once_with(None)

        begin_func_mock.assert_called_once()
        end_func_mock.assert_called_once()

    def test_generator_wrapper_close_call_without_starting_generator(self):
        close_result = 42

        generator_close_func_mock = Mock()
        generator_close_func_mock.side_effect = lambda: close_result

        generator_obj_mock = Mock()
        generator_obj_mock.attach_mock(generator_close_func_mock, 'close')

        begin_func_mock = Mock()
        end_func_mock = Mock()

        generator_wrapper = _GeneratorObjectWrapper(generator_obj_mock, begin_func_mock, end_func_mock)

        self.assertEqual(generator_wrapper.close(), close_result)
        generator_close_func_mock.assert_called_once()

        begin_func_mock.assert_not_called()
        end_func_mock.assert_not_called()

    def test_generator_wrapper_send_call(self):
        send_result = 42

        generator_send_func_mock = Mock()
        generator_send_func_mock.side_effect = lambda x: send_result

        generator_obj_mock = Mock()
        generator_obj_mock.attach_mock(generator_send_func_mock, 'send')

        begin_func_mock = Mock()
        end_func_mock = Mock()

        generator_wrapper = _GeneratorObjectWrapper(generator_obj_mock, begin_func_mock, end_func_mock)
        self.assertEqual(generator_wrapper.send(None), send_result)
        generator_send_func_mock.assert_called_once_with(None)

        self.assertEqual(generator_wrapper.send(None), send_result)
        expected_calls = [
            call(None),
            call(None)
        ]
        generator_send_func_mock.assert_has_calls(expected_calls)

        begin_func_mock.assert_called_once()
        end_func_mock.assert_not_called()

    def test_generator_wrapper_send_call_raised_exception(self):
        exception_type = RuntimeError

        def raise_runtime_exception():
            raise exception_type()

        generator_send_func_mock = Mock()
        generator_send_func_mock.side_effect = lambda x: raise_runtime_exception()

        generator_obj_mock = Mock()
        generator_obj_mock.attach_mock(generator_send_func_mock, 'send')

        begin_func_mock = Mock()
        end_func_mock = Mock()

        generator_wrapper = _GeneratorObjectWrapper(generator_obj_mock, begin_func_mock, end_func_mock)

        with self.assertRaises(exception_type):
            generator_wrapper.send(None)

        generator_send_func_mock.assert_called_once_with(None)

        begin_func_mock.assert_called_once()
        end_func_mock.assert_called_once()

    def test_generator_wrapper_iter_call_propagation_to_send(self):
        send_result = 42

        generator_send_func_mock = Mock()
        generator_send_func_mock.side_effect = lambda x: send_result

        generator_obj_mock = Mock()
        generator_obj_mock.attach_mock(generator_send_func_mock, 'send')

        begin_func_mock = Mock()
        end_func_mock = Mock()

        generator_wrapper = _GeneratorObjectWrapper(generator_obj_mock, begin_func_mock, end_func_mock)
        generator_iterator = iter(generator_wrapper)
        self.assertEqual(next(generator_iterator), send_result)

        generator_send_func_mock.assert_called_once_with(None)

        self.assertEqual(next(generator_iterator), send_result)

        expected_calls = [
            call(None),
            call(None)
        ]
        generator_send_func_mock.assert_has_calls(expected_calls)

        begin_func_mock.assert_called_once()
        end_func_mock.assert_not_called()

    def test_generator_wrapper_throw_call_with_handled_exception(self):
        exception_type = RuntimeError
        throw_result = 42

        generator_throw_func_mock = Mock()
        generator_throw_func_mock.side_effect = lambda x: throw_result

        generator_obj_mock = Mock()
        generator_obj_mock.attach_mock(generator_throw_func_mock, 'throw')

        begin_func_mock = Mock()
        end_func_mock = Mock()

        generator_wrapper = _GeneratorObjectWrapper(generator_obj_mock, begin_func_mock, end_func_mock)

        self.assertEqual(generator_wrapper.throw(exception_type), throw_result)

        generator_throw_func_mock.assert_called_once_with(exception_type)

        begin_func_mock.assert_called_once()
        end_func_mock.assert_not_called()

    def test_generator_wrapper_throw_call_with_unhandled_exception(self):
        exception_type = RuntimeError

        def raise_exception(ex_type):
            raise ex_type()

        generator_throw_func_mock = Mock()
        generator_throw_func_mock.side_effect = raise_exception

        generator_obj_mock = Mock()
        generator_obj_mock.attach_mock(generator_throw_func_mock, 'throw')

        begin_func_mock = Mock()
        end_func_mock = Mock()

        generator_wrapper = _GeneratorObjectWrapper(generator_obj_mock, begin_func_mock, end_func_mock)

        with self.assertRaises(exception_type):
            generator_wrapper.throw(exception_type)

        generator_throw_func_mock.assert_called_once_with(exception_type)

        begin_func_mock.assert_called_once()
        end_func_mock.assert_called_once()


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


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
