from unittest import TestCase

from cabrita.components.watchers import Watch


class TestWatch(TestCase):
    def setUp(self):
        self.watch = Watch()

    def test_interval(self):
        self.assertEqual(self.watch.interval, 30)

    def test__execute(self):
        self.assertRaises(NotImplementedError, self.watch._execute)

    def test_run(self):
        self.assertIsNone(self.watch.run())
