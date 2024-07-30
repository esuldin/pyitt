from unittest import main as unittest_main, TestCase

from ...pyitt_native_mock import patch as pyitt_native_patch
from pyitt.compatibility_layers.itt_python import detach, pause, resume  # pylint: disable=C0411


class CollectionControlTests(TestCase):
    @pyitt_native_patch('detach')
    def test_detach_call(self, detach_mock):
        detach()
        detach_mock.assert_called_once()

    @pyitt_native_patch('pause')
    def test_pause_call(self, pause_mock):
        pause()
        pause_mock.assert_called_once()

    @pyitt_native_patch('resume')
    def test_resume_call(self, resume_mock):
        resume()
        resume_mock.assert_called_once()


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
