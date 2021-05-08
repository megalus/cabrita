import os
from unittest import TestCase, mock

from click.testing import CliRunner

from cabrita.tests import LATEST_CONFIG_PATH


class TestRun(TestCase):
    @mock.patch(
        "cabrita.command.CabritaCommand.execute", side_effect=KeyboardInterrupt()
    )
    @mock.patch("cabrita.run.check_version", return_value="test")
    def test_run(self, *mocks):
        from cabrita.run import run

        os.environ["CABRITA_PATH"] = LATEST_CONFIG_PATH
        runner = CliRunner()
        result = runner.invoke(run)
        self.assertEqual(result.exit_code, 0)

    @mock.patch("cabrita.command.CabritaCommand.execute", side_effect=ValueError())
    @mock.patch("cabrita.run.check_version", return_value="test")
    def test_exception_during_run(self, *mocks):
        from cabrita.run import run

        os.environ["CABRITA_PATH"] = LATEST_CONFIG_PATH
        runner = CliRunner()
        with self.assertRaises(ValueError):
            runner.invoke(run, catch_exceptions=False)
