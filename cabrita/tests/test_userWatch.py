import datetime
from unittest import TestCase, mock

from cabrita.command import CabritaCommand
from cabrita.tests import LATEST_CONFIG_PATH
from cabrita.tests.test_gitInspect import return_git_result


class TestUserWatch(TestCase):
    @classmethod
    def setUpClass(cls):
        command = CabritaCommand(
            cabrita_path=LATEST_CONFIG_PATH, compose_path=(), version="test"
        )
        command.read_compose_files()
        command.prepare_dashboard()
        cls.watch = command.dashboard.user_watches

    @mock.patch("cabrita.components.watchers.run_command", return_value=True)
    @mock.patch("cabrita.abc.utils.run_command", side_effect=return_git_result)
    def test__execute(self, *mocks):
        self.watch.git.run = mocks[0]
        self.watch._execute()
        expected_result = (
            "--------  ------------------  ---------\n"
            "File      [33mcabrita.yml[22m         NOT FOUND\n"
            "--------  ------------------  -------\n"
            "Ping      [32mNgrok Access[22m        [32mUP[22m\n"
            "--------  ------------------  ---------"
        )
        self.assertEqual(self.watch.widget.text, expected_result)

    def test_file(self):
        expected_dict = {
            "cabrita": {
                "dest_path": "$TEST_PROJECT_PATH/config",
                "name": "cabrita.yml",
                "source_name": "cabrita-v2.yml",
                "source_path": "$TEST_PROJECT_PATH",
            }
        }
        self.assertDictEqual(self.watch.file, expected_dict)

    def test_external(self):
        expected_list = []
        self.assertListEqual(self.watch.external, expected_list)

    def test_ping(self):
        expected_dict = {
            "ngrok": {
                "address": "http://localhost:4040",
                "message_on_error": "DOWN",
                "message_on_success": "UP",
                "name": "Ngrok Access",
            }
        }
        self.assertDictEqual(self.watch.ping, expected_dict)

    @mock.patch("cabrita.components.watchers.run_command", return_value=False)
    def test__get_ping_result(self, *mocks):
        self.watch._get_ping_result(self.watch.ping["ngrok"], "ngrok")
        expected_list = ["\x1b[31mNgrok Access\x1b[22m", "\x1b[31mDOWN\x1b[22m"]
        self.assertListEqual(self.watch.result["ping"]["ngrok"], expected_list)

    def test__get_file_result_on_missing_file(self):
        self.watch._get_file_result(self.watch.file["cabrita"], "cabrita")
        expected_list = ["\x1b[33mcabrita.yml\x1b[22m", "NOT FOUND"]
        self.assertListEqual(self.watch.result["file"]["cabrita"], expected_list)

    @mock.patch("os.path.isfile", return_value=True)
    @mock.patch("os.path.getmtime", return_value=datetime.datetime.now())
    def test__get_file_result(self, *mocks):
        self.watch._get_file_result(self.watch.file["cabrita"], "cabrita")
        expected_list = ["\x1b[32mcabrita.yml\x1b[22m", "OK   "]
        self.assertListEqual(self.watch.result["file"]["cabrita"], expected_list)
