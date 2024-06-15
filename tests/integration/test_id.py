from unittest import main as unittest_main, TestCase

from pyitt.native import Domain, Id


class IdTests(TestCase):
    def test_id_creation_without_arguments(self):
        with self.assertRaises(TypeError) as context:
            Id()

        self.assertEqual(str(context.exception), "function missing required argument 'domain' (pos 1)")

    def test_id_creation_with_none(self):
        with self.assertRaises(TypeError) as context:
            Id(None)

        self.assertEqual(str(context.exception), 'The passed domain is not a valid instance of'
                                                 ' pyitt.native.Domain type.')

    def test_id_creation_with_domain(self):
        domain = Domain()
        id_obj = Id(domain)
        self.assertIsNotNone(id_obj)

    def test_id_representation(self):
        domain = Domain()
        id_obj = Id(domain)

        self.assertRegex(repr(id_obj), f'pyitt.native.{Id.__name__}\\(\\d+, \\d+\\)')

    def test_id_representation_for_non_domain_object(self):
        with self.assertRaises(TypeError) as context:
            Id.__repr__(None)  # pylint: disable=C2801

        self.assertEqual(str(context.exception), "descriptor '__repr__' requires a 'pyitt.native.Id' object"
                                                 " but received a 'NoneType'")

    def test_id_string_representation(self):
        domain = Domain()
        id_obj = Id(domain)

        self.assertRegex(str(id_obj), r'\(\d+, \d+\)')

    def test_id_string_representation_for_non_domain_object(self):
        with self.assertRaises(TypeError) as context:
            Id.__str__(None)  # pylint: disable=C2801

        self.assertEqual(str(context.exception), "descriptor '__str__' requires a 'pyitt.native.Id' object"
                                                 " but received a 'NoneType'")


if __name__ == '__main__':
    unittest_main()
