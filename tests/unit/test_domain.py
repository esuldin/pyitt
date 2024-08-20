from unittest import main as unittest_main, TestCase

from .pyitt_native_mock import patch as pyitt_native_patch
import pyitt  # pylint: disable=C0411


class DomainTests(TestCase):
    @pyitt_native_patch('Domain')
    def test_domain_call_without_arguments(self, domain_class_mock):
        pyitt.domain()
        domain_class_mock.assert_called_once_with(None)

    @pyitt_native_patch('Domain')
    def test_domain_call_with_name(self, domain_class_mock):
        name = 'my domain'
        pyitt.domain(name)
        domain_class_mock.assert_called_once_with(name)

    @pyitt_native_patch('Domain')
    def test_domain_creation_without_arguments(self, domain_class_mock):
        pyitt.Domain()
        domain_class_mock.assert_called_once_with()

    @pyitt_native_patch('Domain')
    def test_domain_creation_with_name(self, domain_class_mock):
        name = 'my domain'
        pyitt.Domain(name)
        domain_class_mock.assert_called_once_with(name)


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
