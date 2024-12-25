from unittest import main as unittest_main, TestCase

from pyitt.native import StringHandle, thread_set_name


class ThreadSetNameTests(TestCase):
    def test_thread_set_name_using_none(self):
        with self.assertRaises(TypeError) as context:
            thread_set_name(None)

        self.assertEqual(str(context.exception), f'The passed name is not a valid instance of str or'
                                                 f' pyitt.native.{StringHandle.__name__}.')

    def test_thread_set_name_using_string(self):
        self.assertIsNone(thread_set_name('my thread'))

    def test_thread_set_name_using_string_handle(self):
        thread_name = StringHandle('my thread')
        self.assertIsNone(thread_set_name(thread_name))


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
