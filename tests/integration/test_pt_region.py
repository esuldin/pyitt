from unittest import main as unittest_main, TestCase

from pyitt.native import PTRegion, StringHandle


class PTRegionTests(TestCase):
    def test_pt_region_creation_without_arguments(self):
        region = PTRegion()
        self.assertIsNone(region.name)

    def test_pt_region_creation_with_not_str(self):
        with self.assertRaises(TypeError) as context:
            PTRegion(42)

        self.assertEqual(str(context.exception), f'The passed name is not a valid instance of str or'
                                                 f' pyitt.native.{StringHandle.__name__}.')

    def test_pt_region_creation_with_string(self):
        region_name = 'my region'
        region = PTRegion(region_name)
        self.assertEqual(region.name, region_name)

    def test_pt_region_creation_with_string_handle(self):
        region_name = 'my region'
        region_name_handle = StringHandle(region_name)
        region = PTRegion(region_name_handle)
        self.assertEqual(region.name, region_name)

    def test_pt_region_representation(self):
        region_name = 'my region'
        region = PTRegion(region_name)

        self.assertEqual(repr(region), f"pyitt.native.{PTRegion.__name__}('{region_name}')")

    def test_pt_region_representation_for_non_pt_region_object(self):
        with self.assertRaises(TypeError) as context:
            PTRegion.__repr__(None)  # pylint: disable=C2801

        self.assertEqual(str(context.exception), f"descriptor '__repr__' requires a 'pyitt.native.{PTRegion.__name__}'"
                                                 f" object but received a 'NoneType'")

    def test_pt_region_string_representation(self):
        region_name = 'my region'
        region = PTRegion(region_name)

        self.assertEqual(str(region), region_name)

    def test_pt_region_string_representation_for_non_pt_region_object(self):
        with self.assertRaises(TypeError) as context:
            PTRegion.__str__(None)  # pylint: disable=C2801

        self.assertEqual(str(context.exception), f"descriptor '__str__' requires a 'pyitt.native.{PTRegion.__name__}'"
                                                 f" object but received a 'NoneType'")

    def test_pt_region_begin(self):
        region_name = 'my region'
        region = PTRegion(region_name)

        self.assertIsNone(region.begin())

    def test_pt_region_end(self):
        region_name = 'my region'
        region = PTRegion(region_name)

        self.assertIsNone(region.end())


if __name__ == '__main__':
    unittest_main()
