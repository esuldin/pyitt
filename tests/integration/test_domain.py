from platform import python_implementation
from unittest import main as unittest_main, TestCase

from pyitt.native import Domain, StringHandle


class DomainTests(TestCase):
    def test_domain_creation_without_arguments(self):
        domain = Domain()
        self.assertEqual(domain.name, 'pyitt')

    def test_domain_creation_with_none(self):
        domain = Domain(None)
        self.assertEqual(domain.name, 'pyitt')

    def test_domain_creation_with_string(self):
        domain_name = 'my domain'
        domain = Domain(domain_name)
        self.assertEqual(domain.name, domain_name)

    def test_domain_creation_with_string_handle(self):
        domain_name = 'my domain'
        string_handle = StringHandle(domain_name)
        domain = Domain(string_handle)
        self.assertEqual(domain.name, domain_name)

    def test_domain_creation_with_non_string_object(self):
        with self.assertRaises(TypeError) as context:
            Domain(42)

        self.assertEqual(str(context.exception), f'The passed name is not a valid instance of str or'
                                                 f' pyitt.native.{StringHandle.__name__}.')

    def test_domain_representation(self):
        domain_name = 'my domain'
        domain = Domain(domain_name)

        self.assertEqual(repr(domain), f"pyitt.native.{Domain.__name__}('{domain_name}')")

    def test_domain_representation_for_non_domain_object(self):
        with self.assertRaises(TypeError) as context:
            Domain.__repr__(None)  # pylint: disable=C2801

        if python_implementation() == 'PyPy':
            exception_str = f"The passed object is not a valid instance of pyitt.native.{Domain.__name__} type."
        else:
            exception_str = (f"descriptor '__repr__' requires a 'pyitt.native.{Domain.__name__}' object but received a"
                             f" 'NoneType'")

        self.assertEqual(str(context.exception), exception_str)

    def test_domain_string_representation(self):
        domain_name = 'my domain'
        domain = Domain(domain_name)
        self.assertEqual(str(domain), domain_name)

    def test_domain_string_representation_for_non_domain_object(self):
        with self.assertRaises(TypeError) as context:
            Domain.__str__(None)  # pylint: disable=C2801

        if python_implementation() == 'PyPy':
            exception_str = f"The passed object is not a valid instance of pyitt.native.{Domain.__name__} type."
        else:
            exception_str = (f"descriptor '__str__' requires a 'pyitt.native.{Domain.__name__}' object but received a"
                             f" 'NoneType'")

        self.assertEqual(str(context.exception), exception_str)


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
