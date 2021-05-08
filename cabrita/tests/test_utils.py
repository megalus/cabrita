import os
from pathlib import Path
from unittest import TestCase, mock


class TestUtils(TestCase):
    @mock.patch("cabrita.abc.utils.subprocess.call", return_value=0)
    def test_run_command(self, *args):
        from cabrita.abc.utils import run_command

        test_result = run_command("cd $HOME && ls")
        assert test_result is True

    def test_real_run_command(self):
        from cabrita.abc.utils import run_command

        test_result = run_command("cd $HOME && ls", get_stdout=True)
        assert test_result != ""
        assert isinstance(test_result, str)

    def test_get_path(self):
        from cabrita.abc.utils import get_path

        # Need to check $HOME only for tests in tox
        if not os.getenv("HOME"):
            os.environ["HOME"] = str(Path.home())

        test_path = get_path("$HOME", "")
        assert test_path == str(Path.home())

    def test_format_color(self):
        from cabrita.abc.utils import format_color

        test_text = format_color("Hello World", "warning")
        self.assertEqual(test_text, "\x1b[33mHello World\x1b[22m")
