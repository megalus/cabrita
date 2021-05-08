"""
Git module.

This module has the GitInspect class, which is responsible for
inspect git data from docker services git branches in dashboard.
"""
import os
import re
from enum import Enum
from typing import Tuple

from buzio import formatStr

from cabrita.abc.base import InspectTemplate
from cabrita.abc.utils import persist_on_disk
from cabrita.components.config import Compose

ARROW_UP = "↑"
ARROW_DOWN = "↓"


class GitDirection(Enum):
    """Git direction for branch evaluation.

    Options:
        * **ahead**: check for commits ahead branch
        * **behind**: check for commits behind branch
    """

    ahead = 1
    behind = 2


class GitInspect(InspectTemplate):
    """GitInspect class."""

    def __init__(self, compose: Compose, interval: int, target_branch: str) -> None:
        """Init class."""
        super(GitInspect, self).__init__(compose, interval)
        self.target_branch = target_branch
        self.default_data = None
        self.path = None  # type: str

    def branch_is_dirty(self, path: str = None) -> bool:
        """Check if branch is "dirty".

        Ie.: has non-committed modifications.

        :param path: path for branch

        :return: bool
        """
        if not path:
            path = self.path
        branch_is_dirty = self.run(
            "cd {} && git status --porcelain 2>/dev/null".format(path), get_stdout=True
        )
        return True if branch_is_dirty else False

    def get_git_revision_from_path(self, path, show_branch: bool = False) -> str:
        """Get last tag and most recent commit hash from path.

        :param path: path to search

        :param show_branch: check if add branch name to data

        :return: string
        """
        git_tag = self.run(
            "cd {} && git describe --tags "
            "$(git rev-list --tags --max-count=1 2>/dev/null) "
            "2>/dev/null".format(path),
            get_stdout=True,
        )
        git_hash = self.run(
            "cd {} && git rev-parse --short HEAD 2>/dev/null".format(path),
            get_stdout=True,
        )
        if not git_hash and git_tag:
            return "--"
        if show_branch:
            git_branch = self._get_active_branch(path)
            git_commit_data = "⑂ {}@{}".format(
                git_branch, str(git_hash).replace("\n", "")
            )
        else:
            git_commit_data = "⑂ {}".format(str(git_hash).replace("\n", ""))

        if git_tag:
            git_status = "✎ {}".format(str(git_tag).replace("\n", "")[:15])
        else:
            git_status = git_commit_data

        return git_status

    def get_git_revision(self, service):
        """Return git revision data from service.

        :param service: service name as defined in docker-compose yml.

        :return: string
        """
        if self.compose.is_image(service):
            return "-"
        path = self.compose.get_build_path(service)
        return self.get_git_revision_from_path(path)

    def get_behind_state(self, path):
        """Check if service need pull and return status.

        :param path: path to search.

        :return: string
        """
        if not os.path.isdir(os.path.join(path, ".git")):
            return "OK"

        git_behind = self.run(
            "cd {} && git fetch && git status -bs --porcelain 2> /dev/null".format(
                path
            ),
            get_stdout=True,
        )

        if not git_behind:
            git_state = ""
        elif "behind" in git_behind:
            git_state = formatStr.error("NEED PULL", use_prefix=False)
        else:
            git_state = formatStr.success("OK", use_prefix=False)
        return git_state

    def inspect(self, service: str) -> None:
        """Inspect git data from service.

        If service are not running from a docker image,
        try to find the current branch in service path.
        From this, try to find the relative diff between this branch and target branch

        :param service: service name as defined in docker-compose yml.

        :return: None
        """
        if self.compose.is_image(service):
            return formatStr.info("Using Image", use_prefix=False)

        self.path = self.compose.get_build_path(service)
        branch = self._get_active_branch()

        if branch:
            branch_ahead, branch_behind = self._get_modifications_in_branch()
            (
                target_branch_ahead,
                target_branch_behind,
            ) = self._get_modifications_in_target_branch(branch)

            text = "{}{}{}".format(
                self._get_abbreviate_name(branch),
                formatStr.error(
                    " {} {}".format(ARROW_DOWN, branch_behind), use_prefix=False
                )
                if branch_behind
                else "",
                formatStr.error(
                    " {} {}".format(ARROW_UP, branch_ahead), use_prefix=False
                )
                if branch_ahead
                else "",
            )
            if target_branch_ahead or target_branch_behind:
                text += " ({}{}{})".format(
                    self.target_branch,
                    formatStr.error(
                        " {} {}".format(ARROW_DOWN, target_branch_behind),
                        use_prefix=False,
                    )
                    if target_branch_behind
                    else "",
                    formatStr.error(
                        " {} {}".format(ARROW_UP, target_branch_ahead), use_prefix=False
                    )
                    if target_branch_ahead
                    else "",
                )
            self._status[service] = (
                formatStr.warning(text, use_prefix=False)
                if self.branch_is_dirty()
                else formatStr.success(text, use_prefix=False)
            )
            if target_branch_behind != 0:
                persist_on_disk("add", service, "need_update")
            else:
                persist_on_disk("remove", service, "need_update")
        else:
            self._status[service] = formatStr.error(
                "Branch Not Found", use_prefix=False
            )

    def _get_modifications_in_target_branch(self, branch: str) -> Tuple[int, int]:
        """Return number of commits behind or ahead for target branch on local branch.

        :param branch: current branch name

        :return: typle (int, int)
        """
        if self.target_branch and branch != self.target_branch.replace("origin/", ""):
            target_branch_ahead = self._get_commits_from_target(
                self.path, branch, GitDirection.ahead
            )
            target_branch_behind = self._get_commits_from_target(
                self.path, branch, GitDirection.behind
            )
            return target_branch_ahead, target_branch_behind
        else:
            return 0, 0

    def _get_modifications_in_branch(self) -> Tuple[int, int]:
        """Return number of commits behind or ahead for remote branch for local branch.

        :return: tuple (int, int)
        """
        branch_ahead = self._get_commits(self.path, GitDirection.ahead)
        branch_behind = self._get_commits(self.path, GitDirection.behind)
        return branch_ahead, branch_behind

    def _get_active_branch(self, path: str = None) -> str:
        """Get active branch name.

        :param path: path to search

        :return: string
        """
        if not path:
            path = self.path
        branch = self.run(
            'cd {} && git branch | grep "*" 2>/dev/null'.format(path), get_stdout=True
        )
        return (
            branch.replace("* ", "").replace("\n", "").replace("(", "").replace(")", "")
            if branch
            else ""
        )

    @staticmethod
    def _get_abbreviate_name(full_name) -> str:
        """Abbreviate branch name.

        :param full_name: full branch name

        :return: string
        """
        name = full_name.split("/")[-1]
        if len(name) > 15:
            return "{}...".format(name[:12])
        else:
            return name

    def _get_commits(self, path, direction: GitDirection) -> int:
        """Get number of commits in local branch for informed direction.

        :param path: path to search

        :param direction: git direction for commits

        :return: int
        """
        task = "cd {} && git status -bs --porcelain".format(path)
        ret = self.run(task, get_stdout=True)
        if direction == GitDirection.behind:
            if "behind" in ret:
                s = re.search(r"behind (\d+)", ret)
                return int(s.group(1))
            else:
                return 0
        elif "ahead" in ret:
            s = re.search(r"ahead (\d+)", ret)
            return int(s.group(1))
        else:
            return 0

    def _get_commits_from_target(
        self, path: str, name: str, direction: GitDirection
    ) -> int:
        """Get number of commits based on target branch for informed direction.

        :param path: path to search

        :param name: branch name

        :param direction: git direction for commits

        :return: int
        """
        task = "cd {} && git log {}..{} --oneline 2>/dev/null".format(
            path,
            name if direction == GitDirection.behind else self.target_branch,
            self.target_branch if direction == GitDirection.behind else name,
        )
        ret = self.run(task, get_stdout=True)
        return 0 if not ret else len(ret.split("\n")) - 1
