from unittest import main as unittest_main, TestCase
from unittest.mock import call, Mock

from pyitt._region import _AwaitableObjectWrapper, _GeneratorObjectWrapper  # pylint: disable=C0411


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


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
