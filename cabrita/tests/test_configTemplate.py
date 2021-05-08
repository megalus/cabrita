import os
import tempfile
from unittest import TestCase

from cabrita.components.config import Config
from cabrita.tests import LATEST_CONFIG_PATH


class TestConfigTemplate(TestCase):
    def setUp(self):
        self.maxDiff = None
        self._generate_config()

    def _generate_config(self):
        self.config = Config()
        self.config.add_path(LATEST_CONFIG_PATH)
        self.config.load_file_data()
        self.assertTrue(self.config.is_valid)

    def test_load_not_found_file_data(self):
        self.config.list_path = [("/tmp/bad/path", "")]
        with self.assertRaises(SystemExit) as cm:
            self.config.load_file_data()
        self.assertEqual(cm.exception.code, 127)

    def test_load_bad_file_data(self):
        bad_content = """
            BAD:
             -
            CONTENT
            """

        with tempfile.NamedTemporaryFile("w") as temp:
            temp.write(bad_content)
            temp.flush()
            temp_path = os.path.join(tempfile.gettempdir(), temp.name)
            self.config.list_path = [(temp_path, "")]
            with self.assertRaises(SystemExit) as cm:
                self.config.load_file_data()
            self.assertEqual(cm.exception.code, 1)
