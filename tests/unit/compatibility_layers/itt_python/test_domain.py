from unittest import main as unittest_main, TestCase

from ...pyitt_native_mock import patch as pyitt_native_patch
from pyitt.compatibility_layers.itt_python import domain_create  # pylint: disable=C0411


class DomainTests(TestCase):
    @pyitt_native_patch('Domain')
    def test_domain_create_call(self, domain_mock):
        name = 'my domain'
        self.assertIsNotNone(domain_create(name))
        domain_mock.assert_called_once_with(name)


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
