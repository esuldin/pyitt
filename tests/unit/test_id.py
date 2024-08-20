from unittest import main as unittest_main, TestCase

from .pyitt_native_mock import patch as pyitt_native_patch
import pyitt  # pylint: disable=C0411


class IdTests(TestCase):
    @pyitt_native_patch('Id')
    def test_id_call(self, id_class_mock):
        domain = 'my domain'
        pyitt.id(domain)
        id_class_mock.assert_called_once_with(domain)

    @pyitt_native_patch('Id')
    def test_id_creation(self, id_class_mock):
        domain = 'my domain'
        pyitt.Id(domain)
        id_class_mock.assert_called_once_with(domain)


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
