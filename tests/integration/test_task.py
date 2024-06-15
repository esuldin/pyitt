from unittest import main as unittest_main, TestCase

from pyitt.native import Domain, StringHandle, Id
from pyitt.native import task_begin, task_end, task_begin_overlapped, task_end_overlapped


class TaskBeginTests(TestCase):
    def test_task_begin_without_arguments(self):
        with self.assertRaises(TypeError) as context:
            task_begin()

        self.assertEqual(str(context.exception), 'function takes at least 2 arguments (0 given)')

    def test_task_begin_with_invalid_domain_object(self):
        task_name = StringHandle('my task')

        with self.assertRaises(TypeError) as context:
            task_begin(None, task_name)

        self.assertEqual(str(context.exception), f'The passed domain is not a valid instance of'
                                                 f' pyitt.native.{Domain.__name__} type.')

    def test_task_begin_with_invalid_string_handle_object(self):
        domain = Domain('my domain')

        with self.assertRaises(TypeError) as context:
            task_begin(domain, None)

        self.assertEqual(str(context.exception), f'The passed name is not a valid instance of'
                                                 f' pyitt.native.{StringHandle.__name__} type.')

    def test_task_begin_with_domain_and_name_only(self):
        domain = Domain('my domain')
        task_name = StringHandle('my task')
        self.assertIsNone(task_begin(domain, task_name))

    def test_task_begin_with_domain_and_name_and_ids_as_none(self):
        domain = Domain('my domain')
        task_name = StringHandle('my task')
        self.assertIsNone(task_begin(domain, task_name, None, None))

    def test_task_begin_with_domain_and_name_and_id(self):
        domain = Domain('my domain')
        task_name = StringHandle('my task')
        task_id = Id(domain)
        self.assertIsNone(task_begin(domain, task_name, task_id))

    def test_task_begin_with_invalid_id_object(self):
        domain = Domain('my domain')
        task_name = StringHandle('my task')

        with self.assertRaises(TypeError) as context:
            task_begin(domain, task_name, 42)

        self.assertEqual(str(context.exception), f'The passed id is not a valid instance of'
                                                 f' pyitt.native.{Id.__name__} type.')

    def test_task_begin_with_domain_and_name_and_parent_id(self):
        domain = Domain('my domain')
        task_name = StringHandle('my task')
        parent_id = Id(domain)
        self.assertIsNone(task_begin(domain, task_name, None, parent_id))

    def test_task_begin_with_invalid_parent_id_object(self):
        domain = Domain('my domain')
        task_name = StringHandle('my task')

        with self.assertRaises(TypeError) as context:
            task_begin(domain, task_name, None, 42)

        self.assertEqual(str(context.exception), f'The passed parent_id is not a valid instance of'
                                                 f' pyitt.native.{Id.__name__} type.')


class TaskEndTests(TestCase):
    def test_task_end_without_arguments(self):
        with self.assertRaises(TypeError) as context:
            task_end()

        self.assertEqual(str(context.exception), 'function takes exactly 1 argument (0 given)')

    def test_task_end_with_invalid_domain_object(self):
        with self.assertRaises(TypeError) as context:
            task_end(None)

        self.assertEqual(str(context.exception), f'The passed domain is not a valid instance of'
                                                 f' pyitt.native.{Domain.__name__} type.')

    def test_task_end_with_domain(self):
        domain = Domain('my domain')
        self.assertIsNone(task_end(domain))


class TaskBeginOverlappedTests(TestCase):
    def test_task_begin_overlapped_without_arguments(self):
        with self.assertRaises(TypeError) as context:
            task_begin_overlapped()

        self.assertEqual(str(context.exception), 'function takes at least 3 arguments (0 given)')

    def test_task_begin_overlapped_with_invalid_domain_object(self):
        domain = Domain('my domain')
        task_name = StringHandle('my task')
        task_id = Id(domain)

        with self.assertRaises(TypeError) as context:
            task_begin_overlapped(None, task_name, task_id)

        self.assertEqual(str(context.exception), f'The passed domain is not a valid instance of'
                                                 f' pyitt.native.{Domain.__name__} type.')

    def test_task_begin_overlapped_with_invalid_string_handle_object(self):
        domain = Domain('my domain')
        task_id = Id(domain)

        with self.assertRaises(TypeError) as context:
            task_begin_overlapped(domain, None, task_id)

        self.assertEqual(str(context.exception), f'The passed name is not a valid instance of'
                                                 f' pyitt.native.{StringHandle.__name__} type.')

    def test_task_begin_overlapped_with_invalid_id_object(self):
        domain = Domain('my domain')
        task_name = StringHandle('my task')

        with self.assertRaises(TypeError) as context:
            task_begin_overlapped(domain, task_name, None)

        self.assertEqual(str(context.exception), f'The passed id is not a valid instance of'
                                                 f' pyitt.native.{Id.__name__} type.')

    def test_task_begin_overlapped_with_domain_and_name_and_id_only(self):
        domain = Domain('my domain')
        task_name = StringHandle('my task')
        task_id = Id(domain)
        self.assertIsNone(task_begin_overlapped(domain, task_name, task_id))

    def test_task_begin_overlapped_with_parent_id_as_none(self):
        domain = Domain('my domain')
        task_name = StringHandle('my task')
        task_id = Id(domain)
        self.assertIsNone(task_begin_overlapped(domain, task_name, task_id, None))

    def test_task_begin_with_domain_and_name_and_id_and_parent_id(self):
        domain = Domain('my domain')
        task_name = StringHandle('my task')
        task_id = Id(domain)
        parent_id = Id(domain)
        self.assertIsNone(task_begin_overlapped(domain, task_name, task_id, parent_id))

    def test_task_begin_with_invalid_parent_id_object(self):
        domain = Domain('my domain')
        task_name = StringHandle('my task')
        task_id = Id(domain)

        with self.assertRaises(TypeError) as context:
            task_begin_overlapped(domain, task_name, task_id, 42)

        self.assertEqual(str(context.exception), f'The passed parent_id is not a valid instance of'
                                                 f' pyitt.native.{Id.__name__} type.')


class TaskEndOverlappedTests(TestCase):
    def test_task_end_overlapped_without_arguments(self):
        with self.assertRaises(TypeError) as context:
            task_end_overlapped()

        self.assertEqual(str(context.exception), 'function takes exactly 2 arguments (0 given)')

    def test_task_end_overlapped_with_invalid_domain_object(self):
        domain = Domain('my domain')
        task_id = Id(domain)

        with self.assertRaises(TypeError) as context:
            task_end_overlapped(None, task_id)

        self.assertEqual(str(context.exception), f'The passed domain is not a valid instance of'
                                                 f' pyitt.native.{Domain.__name__} type.')

    def test_task_begin_overlapped_with_invalid_id_object(self):
        domain = Domain('my domain')

        with self.assertRaises(TypeError) as context:
            task_end_overlapped(domain, None)

        self.assertEqual(str(context.exception), f'The passed id is not a valid instance of'
                                                 f' pyitt.native.{Id.__name__} type.')

    def test_task_end_with_domain_and_id(self):
        domain = Domain('my domain')
        task_id = Id(domain)

        self.assertIsNone(task_end_overlapped(domain, task_id))


if __name__ == '__main__':
    unittest_main()
