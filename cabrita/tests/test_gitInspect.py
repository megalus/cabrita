from typing import Union
from unittest import TestCase, mock

from cabrita.command import CabritaCommand
from cabrita.tests import LATEST_CONFIG_PATH


def return_git_result(*args, **kwargs) -> Union[str, bool]:
    command = args[0]
    if "describe" in command:
        return "2.0.1"
    if "rev-parse" in command:
        return "457ac8c"
    if "branch" in command:
        return "* develop"
    if "status" in command:
        return """
            ## 2.0...origin/2.0 [ahead 1, behind 2]
             M cabrita/tests/test_dockerInspect.py
             M cabrita/tests/test_gitInspect.py
             M requirements.txt
            """
    if "log" in command:
        return """
            8fbc901 (HEAD -> 2.0) fix: [WIP] Add tests
            457ac8c Add tox.ini
            6d65d55 fix: [WIP] Add tests
            """
    return False


class TestGitInspect(TestCase):
    @classmethod
    def setUpClass(cls):
        command = CabritaCommand(
            cabrita_path=LATEST_CONFIG_PATH, compose_path=(), version="test"
        )
        command.read_compose_files()
        command.prepare_dashboard()
        cls.git = command.dashboard.all_boxes[-1].git

    @mock.patch("cabrita.abc.utils.run_command", side_effect=return_git_result)
    def test_get_git_revision_from_path(self, *mocks):
        self.git.run = mocks[0]
        test_string = self.git.get_git_revision_from_path(path="/", show_branch=True)
        self.assertEqual(test_string, "✎ 2.0.1")

    @mock.patch("cabrita.abc.utils.run_command", side_effect=return_git_result)
    def test_get_git_revision(self, *mocks):
        self.git.run = mocks[0]
        test_revision = self.git.get_git_revision("django")
        self.assertEqual(test_revision, "✎ 2.0.1")

    @mock.patch("os.path.isdir", return_value=True)
    @mock.patch("cabrita.abc.utils.run_command", side_effect=return_git_result)
    def test_get_behind_state(self, *mocks):
        self.git.run = mocks[0]
        test_behind = self.git.get_behind_state("/")
        self.assertEqual(test_behind, "[31mNEED PULL[22m")

    @mock.patch("cabrita.components.git.persist_on_disk")
    @mock.patch("cabrita.abc.utils.run_command", side_effect=return_git_result)
    def test_inspect(self, *mocks):
        self.git.run = mocks[0]
        self.git.inspect("django")
        expected_result = (
            "[33mdevelop[31m ↓ 2[22m[31m "
            "↑ 1[22m (origin/master[31m ↓ 4[22"
            "m[31m ↑ 4[22m)[22m"
        )
        self.assertEqual(self.git.status("django"), expected_result)

    @mock.patch("cabrita.abc.utils.run_command", side_effect=return_git_result)
    def test__get_modifications_in_target_branch(self, *mocks):
        self.git.run = mocks[0]
        self.git.path = "/"
        result = self.git._get_modifications_in_target_branch("django")
        self.assertEqual(result, (4, 4))

    @mock.patch("cabrita.abc.utils.run_command", side_effect=return_git_result)
    def test__get_modifications_in_branch(self, *mocks):
        self.git.run = mocks[0]
        self.git.path = "/"
        result = self.git._get_modifications_in_branch()
        self.assertEqual(result, (1, 2))

    @mock.patch("cabrita.abc.utils.run_command", side_effect=return_git_result)
    def test__get_active_branch(self, *mocks):
        self.git.run = mocks[0]
        result = self.git._get_active_branch("/")
        self.assertEqual(result, "develop")

    def test__get_abbreviate_name(self):
        long_branch_name = "origin/very_long_branch_name"
        result = self.git._get_abbreviate_name(long_branch_name)
        self.assertEqual(result, "very_long_br...")

    @mock.patch("cabrita.abc.utils.run_command", side_effect=return_git_result)
    def test__get_commits(self, *mocks):
        from cabrita.components.git import GitDirection

        self.git.run = mocks[0]
        result_ahead = self.git._get_commits("/", GitDirection.ahead)
        result_behind = self.git._get_commits("/", GitDirection.behind)
        self.assertEqual(result_ahead, 1)
        self.assertEqual(result_behind, 2)

    @mock.patch("cabrita.abc.utils.run_command", side_effect=return_git_result)
    def test__get_commits_from_target(self, *mocks):
        from cabrita.components.git import GitDirection

        self.git.run = mocks[0]
        result_ahead = self.git._get_commits_from_target(
            "/", "django", GitDirection.ahead
        )
        result_behind = self.git._get_commits_from_target(
            "/", "django", GitDirection.behind
        )
        self.assertEqual(result_ahead, 4)
        self.assertEqual(result_behind, 4)
