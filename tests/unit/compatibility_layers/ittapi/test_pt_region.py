from inspect import stack
from os.path import basename
from unittest import main as unittest_main, TestCase
from unittest.mock import call

from ...pyitt_native_mock import patch as pyitt_native_patch
import pyitt.compatibility_layers.ittapi as ittapi  # pylint: disable=C0411


class PTRegionCreationTests(TestCase):
    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_creation_with_default_constructor(self, pt_region_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        region = ittapi.pt_region()
        caller = stack()[0]
        expected_name = f'{basename(caller.filename)}:{caller.lineno-1}'

        pt_region_class_mock.assert_not_called()

        region.begin()

        pt_region_class_mock.assert_called_once_with(expected_name)
        self.assertEqual(region.name(), expected_name)

    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_creation_as_decorator_for_function(self, pt_region_class_mock, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        @ittapi.pt_region
        def my_function():
            pass  # pragma: no cover

        pt_region_class_mock.assert_called_once_with(my_function.__qualname__)

    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_creation_as_decorator_with_name_for_function(self, pt_region_class_mock,
                                                                    string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        @ittapi.pt_region('my function')
        def my_function():
            pass  # pragma: no cover

        pt_region_class_mock.assert_called_once_with('my function')


class PTRegionPropertiesTest(TestCase):
    @pyitt_native_patch('StringHandle')
    def test_pt_region_properties(self, string_handle_class_mock):
        string_handle_class_mock.side_effect = lambda x: x

        name = 'my pt region'
        region = ittapi.pt_region(name)

        self.assertIs(region.get_pt_region(), region)
        self.assertEqual(region.name(), name)

        self.assertEqual(str(region), name)
        self.assertEqual(repr(region), f'{region.__class__.__name__}(\'{name}\')')


class PTRegionExecutionTests(TestCase):
    @pyitt_native_patch('PTRegion')
    @pyitt_native_patch('StringHandle')
    def test_pt_region_for_function(self, pt_region_class_mock, string_handle_class_mock):
        string_handle_class_mock.return_value = 'string_handle'

        @ittapi.pt_region
        def my_function():
            return 42

        string_handle_class_mock.assert_called_once_with(my_function.__qualname__)
        pt_region_class_mock.assert_called_once_with(string_handle_class_mock.return_value)

        self.assertEqual(my_function(), 42)

        expected_calls = [call().begin(),
                          call().end()]
        pt_region_class_mock.assert_has_calls(expected_calls)


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
