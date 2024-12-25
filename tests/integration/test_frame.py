from unittest import main as unittest_main, TestCase

from pyitt.native import Domain, Id
from pyitt.native import frame_begin, frame_end


class TaskBeginTests(TestCase):
    def test_frame_begin_without_arguments(self):
        with self.assertRaises(TypeError) as context:
            frame_begin()

        self.assertEqual(str(context.exception), 'function takes at least 1 argument (0 given)')

    def test_frame_begin_with_invalid_domain_object(self):
        with self.assertRaises(TypeError) as context:
            frame_begin(None)

        self.assertEqual(str(context.exception), f'The passed domain is not a valid instance of'
                                                 f' pyitt.native.{Domain.__name__} type.')

    def test_frame_begin_with_domain_only(self):
        domain = Domain('my domain')
        self.assertIsNone(frame_begin(domain))

    def test_frame_begin_with_domain_and_id_as_none(self):
        domain = Domain('my domain')
        self.assertIsNone(frame_begin(domain, None))

    def test_frame_begin_with_domain_and_id(self):
        domain = Domain('my domain')
        frame_id = Id(domain)
        self.assertIsNone(frame_begin(domain, frame_id))

    def test_frame_begin_with_invalid_id_object(self):
        domain = Domain('my domain')

        with self.assertRaises(TypeError) as context:
            frame_begin(domain, 42)

        self.assertEqual(str(context.exception), f'The passed id is not a valid instance of'
                                                 f' pyitt.native.{Id.__name__} type.')


class TaskEndTests(TestCase):
    def test_frame_end_without_arguments(self):
        with self.assertRaises(TypeError) as context:
            frame_end()

        self.assertEqual(str(context.exception), 'function takes at least 1 argument (0 given)')

    def test_frame_end_with_invalid_domain_object(self):
        with self.assertRaises(TypeError) as context:
            frame_end(None)

        self.assertEqual(str(context.exception), f'The passed domain is not a valid instance of'
                                                 f' pyitt.native.{Domain.__name__} type.')

    def test_frame_end_with_domain_only(self):
        domain = Domain('my domain')
        self.assertIsNone(frame_end(domain))

    def test_frame_end_with_domain_and_id_as_none(self):
        domain = Domain('my domain')
        self.assertIsNone(frame_end(domain, None))

    def test_frame_end_with_domain_and_id(self):
        domain = Domain('my domain')
        frame_id = Id(domain)
        self.assertIsNone(frame_end(domain, frame_id))

    def test_frame_end_with_invalid_id_object(self):
        domain = Domain('my domain')

        with self.assertRaises(TypeError) as context:
            frame_end(domain, 42)

        self.assertEqual(str(context.exception), f'The passed id is not a valid instance of'
                                                 f' pyitt.native.{Id.__name__} type.')


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
