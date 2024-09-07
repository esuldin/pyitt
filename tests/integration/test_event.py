from platform import python_implementation
from unittest import main as unittest_main, TestCase

from pyitt.native import Event, StringHandle


class EventTests(TestCase):
    def test_event_creation_without_arguments(self):
        with self.assertRaises(TypeError) as context:
            Event()

        self.assertEqual(str(context.exception), "function missing required argument 'name' (pos 1)")

    def test_event_creation_with_none(self):
        with self.assertRaises(TypeError) as context:
            Event(None)

        self.assertEqual(str(context.exception), f'The passed name is not a valid instance of str or'
                                                 f' pyitt.native.{StringHandle.__name__}.')

    def test_event_creation_with_string(self):
        event_name = 'my event'
        event = Event(event_name)
        self.assertEqual(event.name, event_name)

    def test_event_creation_with_string_handle(self):
        event_name = 'my event'
        event_name_handle = StringHandle(event_name)
        event = Event(event_name_handle)
        self.assertEqual(event.name, event_name)

    def test_event_representation(self):
        event_name = 'my event'
        event = Event(event_name)

        self.assertEqual(repr(event), f"pyitt.native.{Event.__name__}('{event_name}')")

    def test_event_representation_for_non_event_object(self):
        with self.assertRaises(TypeError) as context:
            Event.__repr__(None)  # pylint: disable=C2801

        if python_implementation() == 'PyPy':
            exception_str = f"The passed object is not a valid instance of pyitt.native.{Event.__name__} type."
        else:
            exception_str = (f"descriptor '__repr__' requires a 'pyitt.native.{Event.__name__}' object but received a"
                             f" 'NoneType'")

        self.assertEqual(str(context.exception), exception_str)

    def test_event_string_representation(self):
        event_name = 'my event'
        event = Event(event_name)

        self.assertEqual(str(event), event_name)

    def test_event_string_representation_for_non_event_object(self):
        with self.assertRaises(TypeError) as context:
            Event.__str__(None)  # pylint: disable=C2801

        if python_implementation() == 'PyPy':
            exception_str = f"The passed object is not a valid instance of pyitt.native.{Event.__name__} type."
        else:
            exception_str = (f"descriptor '__str__' requires a 'pyitt.native.{Event.__name__}' object but received a"
                             f" 'NoneType'")

        self.assertEqual(str(context.exception), exception_str)

    def test_event_begin(self):
        event_name = 'my event'
        event = Event(event_name)

        self.assertIsNone(event.begin())

    def test_event_end(self):
        event_name = 'my event'
        event = Event(event_name)

        self.assertIsNone(event.end())


if __name__ == '__main__':
    unittest_main()
