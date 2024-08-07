from unittest import main as unittest_main, TestCase

# pylint: disable=C0411
from .pyitt_native_mock import patch as pyitt_native_patch
from pyitt.collection_control import _CollectionRegion
import pyitt


class DirectCollectionControlTests(TestCase):
    @pyitt_native_patch('detach')
    def test_detach_call(self, detach_mock):
        pyitt.collection_control.detach()
        detach_mock.assert_called_once()

    @pyitt_native_patch('pause')
    def test_pause_call(self, pause_mock):
        pyitt.collection_control.pause()
        pause_mock.assert_called_once()

    @pyitt_native_patch('resume')
    def test_resume_call(self, resume_mock):
        pyitt.collection_control.resume()
        resume_mock.assert_called_once()


class CollectionRegionAbstractMethodsTest(TestCase):
    def test_region_abstract_method_begin(self):
        with self.assertRaises(NotImplementedError):
            _CollectionRegion._begin(_CollectionRegion())  # pylint: disable=W0212

    def test_region_abstract_method_end(self):
        with self.assertRaises(NotImplementedError):
            _CollectionRegion._end(_CollectionRegion())  # pylint: disable=W0212


class ActiveRegionTests(TestCase):
    @pyitt_native_patch('pause')
    @pyitt_native_patch('resume')
    def test_active_region_as_decorator(self, pause_mock, resume_mock):
        @pyitt.active_region
        def my_function():
            return 42

        self.assertEqual(my_function(), 42)
        resume_mock.assert_called_once()
        pause_mock.assert_called_once()

    @pyitt_native_patch('pause')
    @pyitt_native_patch('resume')
    def test_active_region_as_context_manager(self, pause_mock, resume_mock):
        with pyitt.active_region():
            pass

        resume_mock.assert_called_once()
        pause_mock.assert_called_once()

    @pyitt_native_patch('pause')
    @pyitt_native_patch('resume')
    def test_active_region_with_manual_activation(self, pause_mock, resume_mock):
        region = pyitt.active_region()

        region.activator.deactivate()
        with region:
            pass

        resume_mock.assert_not_called()
        pause_mock.assert_not_called()

        region.activator.activate()
        with region:
            pass

        resume_mock.assert_called_once()
        pause_mock.assert_called_once()

    @pyitt_native_patch('pause')
    @pyitt_native_patch('resume')
    def test_active_region_with_custom_activator(self, pause_mock, resume_mock):
        for i in range(4):
            with pyitt.active_region(activator=lambda: i % 2):  # pylint: disable=W0640
                pass

        self.assertEqual(resume_mock.call_count, 2)
        self.assertEqual(pause_mock.call_count, 2)

    @pyitt_native_patch('pause')
    @pyitt_native_patch('resume')
    def test_active_region_as_decorator_without_activator(self, pause_mock, resume_mock):
        @pyitt.active_region(activator=None)
        def my_function():
            return 42

        self.assertEqual(my_function(), 42)
        resume_mock.assert_called_once()
        pause_mock.assert_called_once()


class PausedRegionTests(TestCase):
    @pyitt_native_patch('pause')
    @pyitt_native_patch('resume')
    def test_paused_region_as_decorator(self, pause_mock, resume_mock):
        @pyitt.paused_region
        def my_function():
            return 42

        self.assertEqual(my_function(), 42)
        resume_mock.assert_called_once()
        pause_mock.assert_called_once()

    @pyitt_native_patch('pause')
    @pyitt_native_patch('resume')
    def test_paused_region_as_context_manager(self, pause_mock, resume_mock):
        with pyitt.paused_region():
            pass

        resume_mock.assert_called_once()
        pause_mock.assert_called_once()

    @pyitt_native_patch('pause')
    @pyitt_native_patch('resume')
    def test_paused_region_with_manual_activation(self, pause_mock, resume_mock):
        region = pyitt.paused_region()

        region.activator.deactivate()
        with region:
            pass

        resume_mock.assert_not_called()
        pause_mock.assert_not_called()

        region.activator.activate()
        with region:
            pass

        resume_mock.assert_called_once()
        pause_mock.assert_called_once()

    @pyitt_native_patch('pause')
    @pyitt_native_patch('resume')
    def test_paused_region_with_custom_activator(self, pause_mock, resume_mock):
        for i in range(4):
            with pyitt.paused_region(activator=lambda: i % 2):  # pylint: disable=W0640
                pass

        self.assertEqual(resume_mock.call_count, 2)
        self.assertEqual(pause_mock.call_count, 2)

    @pyitt_native_patch('pause')
    @pyitt_native_patch('resume')
    def test_paused_region_as_decorator_without_activator(self, pause_mock, resume_mock):
        @pyitt.paused_region(activator=None)
        def my_function():
            return 42

        self.assertEqual(my_function(), 42)
        resume_mock.assert_called_once()
        pause_mock.assert_called_once()


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
