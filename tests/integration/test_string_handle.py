from unittest import main as unittest_main, TestCase

from pyitt.native import StringHandle


class StringHandleTests(TestCase):
    def test_string_handle_creation_without_arguments(self):
        with self.assertRaises(TypeError) as context:
            StringHandle()

        self.assertEqual(str(context.exception), "function missing required argument 'str' (pos 1)")

    def test_string_handle_creation_with_none(self):
        with self.assertRaises(TypeError) as context:
            StringHandle(None)

        self.assertEqual(str(context.exception), 'The passed string is not a valid instance of str type.')

    def test_string_handle_creation_with_string(self):
        s = 'my str'
        str_handle = StringHandle(s)

        self.assertEqual(str_handle._str, s)  # pylint: disable=W0212

    def test_string_handle_representation(self):
        s = 'my str'
        str_handle = StringHandle(s)

        self.assertEqual(repr(str_handle), f"pyitt.native.{StringHandle.__name__}('{s}')")

    def test_string_handle_representation_for_non_domain_object(self):
        with self.assertRaises(TypeError) as context:
            StringHandle.__repr__(None)  # pylint: disable=C2801

        self.assertEqual(str(context.exception), "descriptor '__repr__' requires a 'pyitt.native.StringHandle' object"
                                                 " but received a 'NoneType'")

    def test_string_handle_string_representation(self):
        s = 'my str'
        str_handle = StringHandle(s)

        self.assertEqual(str(str_handle), s)

    def test_string_handle_string_representation_for_non_domain_object(self):
        with self.assertRaises(TypeError) as context:
            StringHandle.__str__(None)  # pylint: disable=C2801

        self.assertEqual(str(context.exception), "descriptor '__str__' requires a 'pyitt.native.StringHandle' object"
                                                 " but received a 'NoneType'")


if __name__ == '__main__':
    unittest_main()
