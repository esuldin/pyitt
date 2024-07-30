from unittest import main as unittest_main, TestCase
from unittest.mock import Mock

from ...pyitt_native_mock import patch as pyitt_native_patch
# pylint: disable=C0411
from pyitt.compatibility_layers.itt_python import pt_region_create, pt_region_begin, pt_region_end


class PTRegionTests(TestCase):
    @pyitt_native_patch('PTRegion')
    def test_pt_region_creation_with_default_constructor(self, pt_region_class_mock):
        name = 'my pt region'
        self.assertIsNotNone(pt_region_create(name))
        pt_region_class_mock.assert_called_once_with(name)

    def test_pt_region_begin_call(self):
        region = Mock()
        self.assertIsNone(pt_region_begin(region))
        region.begin.assert_called_once_with()

    def test_pt_region_end_call(self):
        region = Mock()
        self.assertIsNone(pt_region_end(region))
        region.end.assert_called_once_with()


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
