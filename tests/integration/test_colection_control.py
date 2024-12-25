from unittest import main as unittest_main, TestCase

from pyitt.native import pause, resume, detach


class CollectionControlTests(TestCase):
    def test_pause(self):
        self.assertIsNone(pause())

    def test_resume(self):
        self.assertIsNone(resume())

    def test_detach(self):
        self.assertIsNone(detach())


if __name__ == '__main__':
    unittest_main()  # pragma: no cover
