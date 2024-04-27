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
        domain_name = 'My Domain'
        domain = Domain(domain_name)
        self.assertEqual(domain.name, domain_name)

    def test_domain_creation_with_string_handle(self):
        domain_name = 'My Domain'
        string_handle = StringHandle(domain_name)
        domain = Domain(string_handle)
        self.assertEqual(domain.name, domain_name)

    def test_domain_creation_with_non_string_object(self):
        with self.assertRaises(TypeError) as context:
            Domain(42)

        self.assertEqual(str(context.exception), 'The passed name is not a valid instance of str or'
                                                 ' pyitt.native.StringHandle.')


if __name__ == '__main__':
    unittest_main()
