from platform import python_implementation
from unittest import main as unittest_main, TestCase

from pyitt.native import Counter, Domain, StringHandle


class CounterTests(TestCase):
    def test_counter_creation_without_arguments(self):
        with self.assertRaises(TypeError) as context:
            Counter()

        self.assertEqual(str(context.exception), "function missing required argument 'name' (pos 1)")

    def test_counter_creation_with_none(self):
        with self.assertRaises(TypeError) as context:
            Counter(None)

        self.assertEqual(str(context.exception), f'The passed name is not a valid instance of str or'
                                                 f' pyitt.native.{StringHandle.__name__}.')

    def test_counter_creation_with_string(self):
        name = 'my counter'
        counter = Counter(name)
        self.assertEqual(counter.name, name)

    def test_counter_creation_with_string_handle(self):
        name = 'my counter'
        name_handle = StringHandle(name)
        counter = Counter(name_handle)
        self.assertEqual(counter.name, name)

    def test_counter_creation_with_domain_none(self):
        name = 'my counter'
        counter = Counter(name, None)
        self.assertEqual(counter.name, name)
        self.assertIsNotNone(counter.domain)

    def test_counter_creation_with_domain(self):
        name = 'my counter'
        domain = Domain()
        counter = Counter(name, domain)
        self.assertEqual(counter.name, name)
        self.assertIs(counter.domain, domain)

    def test_counter_creation_with_non_domain_obj(self):
        name = 'my counter'

        with self.assertRaises(ValueError) as context:
            Counter(name, 42)

        self.assertEqual(str(context.exception), f'The pyitt.native.{Domain.__name__} object cannot be created for the'
                                                 f' instance of pyitt.native.{Counter.__name__}.')

        self.assertTrue(hasattr(context.exception, '__cause__'))
        self.assertIsInstance(context.exception.__cause__, BaseException)

    def test_counter_creation_with_domain_and_value(self):
        name = 'my counter'
        domain = Domain()
        value = 42
        counter = Counter(name, domain, value)
        self.assertEqual(counter.name, name)
        self.assertIs(counter.domain, domain)
        self.assertEqual(counter.value, value)

    def test_counter_creation_with_domain_and_non_int_value(self):
        name = 'my counter'
        domain = Domain()

        with self.assertRaises(TypeError) as context:
            Counter(name, domain, '')

        self.assertEqual(str(context.exception), 'The passed value is not a valid instance of int and cannot be'
                                                 ' converted to int.')

    def test_counter_creation_with_value_conversion(self):
        name = 'my counter'
        value = 42.2
        counter = Counter(name, value=value)
        self.assertEqual(counter.name, name)
        self.assertEqual(counter.value, int(value))

    def test_counter_representation(self):
        name = 'my event'
        domain = Domain('my domain')
        value = 42
        counter = Counter(name, domain, value)

        self.assertEqual(repr(counter),
                         f"pyitt.native.{Counter.__name__}({repr(name)}, {repr(domain)}, {repr(value)})")

    def test_counter_representation_for_non_counter_object(self):
        with self.assertRaises(TypeError) as context:
            Counter.__repr__(None)  # pylint: disable=C2801

        if python_implementation() == 'PyPy':
            exception_str = f"The passed object is not a valid instance of pyitt.native.{Counter.__name__} type."
        else:
            exception_str = (f"descriptor '__repr__' requires a 'pyitt.native.{Counter.__name__}' object but received a"
                             f" 'NoneType'")

        self.assertEqual(str(context.exception), exception_str)

    def test_counter_string_representation(self):
        name = 'my event'
        domain = Domain('my domain')
        value = 42
        counter = Counter(name, domain, value)

        self.assertEqual(str(counter), f"{{ name: '{str(name)}', domain: '{str(domain)}', value: {str(value)} }}")

    def test_counter_string_representation_for_non_counter_object(self):
        with self.assertRaises(TypeError) as context:
            Counter.__str__(None)  # pylint: disable=C2801

        if python_implementation() == 'PyPy':
            exception_str = f"The passed object is not a valid instance of pyitt.native.{Counter.__name__} type."
        else:
            exception_str = (f"descriptor '__str__' requires a 'pyitt.native.{Counter.__name__}' object but received a"
                             f" 'NoneType'")

        self.assertEqual(str(context.exception), exception_str)

    def test_counter_set(self):
        counter = Counter('my counter')
        value = 42
        self.assertIsNone(counter.set(value))
        self.assertEqual(counter.value, value)

    def test_counter_set_with_non_int_value(self):
        counter = Counter('my counter')
        with self.assertRaises(ValueError) as context:
            counter.set('')

        self.assertEqual(str(context.exception), 'The passed value is not a valid instance of int and cannot be'
                                                 ' converted to int.')

    def test_counter_set_for_non_counter_object(self):
        with self.assertRaises(TypeError) as context:
            Counter.set(None, 42)

        if python_implementation() == 'PyPy':
            exception_str = (f"descriptor 'set' requires a 'pyitt.native.{Counter.__name__}' object but received a"
                             f" 'NoneType'")
        else:
            exception_str = (f"descriptor 'set' for 'pyitt.native.{Counter.__name__}' objects doesn't apply to a"
                             f" 'NoneType' object")

        self.assertEqual(str(context.exception), exception_str)

    def test_counter_inc(self):
        counter = Counter('my counter')
        self.assertIsNone(counter.inc())
        self.assertEqual(counter.value, 1)

    def test_counter_inc_with_specified_value(self):
        counter = Counter('my counter')
        value = 42
        self.assertIsNone(counter.inc(value))
        self.assertEqual(counter.value, value)
        self.assertIsNone(counter.inc(value))
        self.assertEqual(counter.value, value + value)

    def test_counter_inc_with_non_int_value(self):
        counter = Counter('my counter')
        with self.assertRaises(ValueError) as context:
            counter.inc('')

        self.assertEqual(str(context.exception), 'The passed delta is not a valid instance of int and cannot be'
                                                 ' converted to int.')

    def test_counter_inc_for_non_counter_object(self):
        with self.assertRaises(TypeError) as context:
            Counter.inc(None, 42)

        if python_implementation() == 'PyPy':
            exception_str = (f"descriptor 'inc' requires a 'pyitt.native.{Counter.__name__}' object but received a"
                             f" 'NoneType'")
        else:
            exception_str = (f"descriptor 'inc' for 'pyitt.native.{Counter.__name__}' objects doesn't apply to a"
                             f" 'NoneType' object")

        self.assertEqual(str(context.exception), exception_str)

    def test_counter_dec(self):
        value = 42
        counter = Counter('my counter', value=value)
        self.assertIsNone(counter.dec())
        self.assertEqual(counter.value, value - 1)

    def test_counter_dec_with_specified_value(self):
        value = 42
        counter = Counter('my counter', value=value * 2)
        self.assertIsNone(counter.dec(value))
        self.assertEqual(counter.value, value)
        self.assertIsNone(counter.dec(value))
        self.assertEqual(counter.value, 0)

    def test_counter_dec_negative(self):
        counter = Counter('my counter')
        with self.assertRaises(OverflowError) as context:
            counter.dec()

        if python_implementation() == 'PyPy':
            exception_str = "cannot convert negative integer to unsigned int"
        else:
            exception_str = "can't convert negative int to unsigned"

        self.assertEqual(str(context.exception), exception_str)

    def test_counter_dec_with_non_int_value(self):
        counter = Counter('my counter')
        with self.assertRaises(ValueError) as context:
            counter.dec('')
        self.assertEqual(str(context.exception), 'The passed delta is not a valid instance of int and cannot be'
                                                 ' converted to int.')

    def test_counter_dec_for_non_counter_object(self):
        with self.assertRaises(TypeError) as context:
            Counter.dec(None, 42)

        if python_implementation() == 'PyPy':
            exception_str = (f"descriptor 'dec' requires a 'pyitt.native.{Counter.__name__}' object but received a"
                             f" 'NoneType'")
        else:
            exception_str = (f"descriptor 'dec' for 'pyitt.native.{Counter.__name__}' objects doesn't apply to a"
                             f" 'NoneType' object")

        self.assertEqual(str(context.exception), exception_str)

    def test_counter_inc_inplace(self):
        counter = Counter('my counter')
        value = 42
        counter += value
        self.assertEqual(counter.value, value)
        counter += value
        self.assertEqual(counter.value, value + value)

    def test_counter_inc_inplace_with_non_int_value(self):
        counter = Counter('my counter')
        with self.assertRaises(ValueError) as context:
            counter += ''

        self.assertEqual(str(context.exception), 'The passed delta is not a valid instance of int and cannot be'
                                                 ' converted to int.')

    def test_counter_inc_inplace_for_non_counter_object(self):
        with self.assertRaises(TypeError) as context:
            Counter.__iadd__(None, 42)  # pylint: disable=C2801

        if python_implementation() == 'PyPy':
            exception_str = f"The passed object is not a valid instance of pyitt.native.{Counter.__name__} type."
        else:
            exception_str = (f"descriptor '__iadd__' requires a 'pyitt.native.{Counter.__name__}' object but received a"
                             f" 'NoneType'")

        self.assertEqual(str(context.exception), exception_str)

    def test_counter_dec_inplace(self):
        value = 42
        counter = Counter('my counter', value=value * 2)
        counter -= value
        self.assertEqual(counter.value, value)
        counter -= value
        self.assertEqual(counter.value, 0)

    def test_counter_dec_inplace_negative(self):
        counter = Counter('my counter')
        with self.assertRaises(OverflowError) as context:
            counter -= 1

        if python_implementation() == 'PyPy':
            exception_str = "cannot convert negative integer to unsigned int"
        else:
            exception_str = "can't convert negative int to unsigned"

        self.assertEqual(str(context.exception), exception_str)

    def test_counter_dec_inplace_with_non_int_value(self):
        counter = Counter('my counter')
        with self.assertRaises(ValueError) as context:
            counter -= ''

        self.assertEqual(str(context.exception), 'The passed delta is not a valid instance of int and cannot be'
                                                 ' converted to int.')

    def test_counter_dec_inplace_for_non_counter_object(self):
        with self.assertRaises(TypeError) as context:
            Counter.__isub__(None, 42)  # pylint: disable=C2801

        if python_implementation() == 'PyPy':
            exception_str = f"The passed object is not a valid instance of pyitt.native.{Counter.__name__} type."
        else:
            exception_str = (f"descriptor '__isub__' requires a 'pyitt.native.{Counter.__name__}' object but received a"
                             f" 'NoneType'")

        self.assertEqual(str(context.exception), exception_str)


if __name__ == '__main__':
    unittest_main()
