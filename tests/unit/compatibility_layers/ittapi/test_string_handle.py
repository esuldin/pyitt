from unittest import main as unittest_main, TestCase

from ...pyitt_native_mock import patch as pyitt_native_patch
import pyitt.compatibility_layers.ittapi as ittapi  # pylint: disable=C0411


class StringHandleTests(TestCase):
    @pyitt_native_patch('StringHandle')
    def test_string_handle_call(self, string_handle_class_mock):
        s = 'my string'
        ittapi.string_handle(s)
        string_handle_class_mock.assert_called_once_with(s)

    @pyitt_native_patch('StringHandle')
    def test_string_handle_creation(self, string_handle_class_mock):
        s = 'my string'
        ittapi.StringHandle(s)
        string_handle_class_mock.assert_called_once_with(s)


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
