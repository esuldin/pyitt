from unittest import main as unittest_main, TestCase

# pylint: disable=C0411
from ...pyitt_native_mock import patch as pyitt_native_patch
import pyitt
import pyitt.compatibility_layers.ittapi as ittapi


class DirectCollectionControlTests(TestCase):
    @pyitt_native_patch('detach')
    def test_detach_call(self, detach_mock):
        ittapi.detach()
        detach_mock.assert_called_once()

    @pyitt_native_patch('pause')
    def test_pause_call(self, pause_mock):
        ittapi.pause()
        pause_mock.assert_called_once()

    @pyitt_native_patch('resume')
    def test_resume_call(self, resume_mock):
        ittapi.resume()
        resume_mock.assert_called_once()


class CompatibleCallsTests(TestCase):
    def test_active_region_call_is_same(self):
        self.assertIs(ittapi.active_region, pyitt.active_region)

    def test_paused_region_call_is_same(self):
        self.assertIs(ittapi.paused_region, pyitt.paused_region)

    def test_active_region_class_is_same(self):
        self.assertIs(ittapi.ActiveRegion, pyitt.ActiveRegion)

    def test_paused_region_class_is_same(self):
        self.assertIs(ittapi.PausedRegion, pyitt.PausedRegion)


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
