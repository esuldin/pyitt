from unittest import main as unittest_main, TestCase
from unittest.mock import Mock

from .pyitt_native_mock import patch as pyitt_native_patch
from pyitt import counter  # pylint: disable=C0411


class CounterCreationTests(TestCase):
    @pyitt_native_patch('Counter')
    def test_counter_creation_with_name(self, counter_class_mock):
        counter_mock_obj = Mock()
        counter_class_mock.return_value = counter_mock_obj

        name = 'my counter'
        self.assertIs(counter(name), counter_mock_obj)
        counter_class_mock.assert_called_once_with(name, None, None)

    @pyitt_native_patch('Counter')
    def test_counter_creation_with_name_and_domain(self, counter_class_mock):
        counter_mock_obj = Mock()
        counter_class_mock.return_value = counter_mock_obj

        name = 'my counter'
        domain = Mock()
        self.assertIs(counter(name, domain), counter_mock_obj)
        counter_class_mock.assert_called_once_with(name, domain, None)

    @pyitt_native_patch('Counter')
    def test_counter_creation_with_name_and_domain_and_init_value(self, counter_class_mock):
        counter_mock_obj = Mock()
        counter_class_mock.return_value = counter_mock_obj

        name = 'my counter'
        domain = Mock()
        value = Mock()
        self.assertIs(counter(name, domain, value), counter_mock_obj)
        counter_class_mock.assert_called_once_with(name, domain, value)

    @pyitt_native_patch('Counter')
    def test_counter_creation_with_name_and_init_value(self, counter_class_mock):
        counter_mock_obj = Mock()
        counter_class_mock.return_value = counter_mock_obj

        name = 'my counter'
        value = Mock()
        self.assertIs(counter(name, init_value=value), counter_mock_obj)
        counter_class_mock.assert_called_once_with(name, None, value)


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
