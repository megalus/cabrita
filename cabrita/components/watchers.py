"""Watchers module."""
import os
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List

import psutil
from buzio import formatStr
from dashing import dashing
from tabulate import tabulate

from cabrita.abc.utils import format_color, get_path, run_command
from cabrita.components.box import Box


class Watch(Box):
    """Watch class.

    Base class for watchers based on Box class.
    """

    _interval = 30.0

    @property
    def interval(self) -> float:
        """Return interval in seconds for each update.

        Default: 30 seconds.

        :return: float
        """
        return self._interval

    @interval.setter
    def interval(self, value):
        self._interval = float(value)

    def _execute(self) -> None:
        """Execute method for the class.

        Need to be implement in subclasses.

        :return: None
        """
        raise NotImplementedError()

    def run(self) -> None:
        """Check if watch can update his data and execute the update.

        :return: None
        """
        if not self.can_update:
            return
        self._execute()
        self.last_update = datetime.now()


class DockerComposeWatch(Watch):
    """Docker Compose Watch class.

    Watch for docker-compose file status.
    """

    def __init__(self, **kwargs) -> None:
        """Init class."""
        self.config = kwargs.pop("config")
        self.version = kwargs.pop("version")
        super(DockerComposeWatch, self).__init__(**kwargs)
        self.interval = 15
        self.last_update = datetime.now() - timedelta(seconds=self.interval)

    def _execute(self) -> None:
        """Execute data update for watch.

        :return: None
        """
        table_lines = []
        for file in self.config.compose_files:
            if "override" in file:
                continue
            full_path = self.config.get_compose_path(file, os.path.dirname(file))
            path = os.path.dirname(full_path)
            filename = os.path.splitext(os.path.basename(full_path))[0]

            has_override = [
                obj for obj in self.config.compose_files if "override" in obj
            ]
            if has_override:
                filename += " (override)"

            if self.git.branch_is_dirty(path):
                git_state = format_color("Branch modified", "warning")
                git_revision = self.git.get_git_revision_from_path(
                    path, show_branch=True
                )
                table_data = [filename, git_revision, git_state]
            else:
                git_state = self.git.get_behind_state(path)
                git_revision = self.git.get_git_revision_from_path(
                    path, show_branch=True
                )
                table_data = [filename, git_state, git_revision]

            table_lines.append(table_data)

        table_lines = self.format_revision(table_lines)

        table = tabulate(table_lines, [])

        title = "{}:Cabrita v.{}".format(self.config.title, self.version)
        self._widget = dashing.Text(
            table,
            color=6,
            border_color=5,
            background_color=self.background_color,
            title=title,
        )


class UserWatch(Watch):
    """User Watch class.

    Watch for user defined watchers in cabrita.yml.
    """

    def __init__(self, **kwargs) -> None:
        """Init class."""
        self.config = kwargs.pop("config")
        super(UserWatch, self).__init__(**kwargs)
        self._watchers = self.config.watchers
        self.result = {"file": {}, "external": {}, "ping": {}}  # type: Dict[Any, dict]
        self.last_update = datetime.now() - timedelta(seconds=self.interval)

    def _execute(self) -> None:
        """Execute data update for each user watch.

        :return: None
        """
        if not self.file and not self.ping:
            self._widget = dashing.Text(
                "No Watchers configured.",
                color=6,
                border_color=5,
                background_color=self.background_color,
                title="Watchers",
            )
            return

        for watch in self.file:
            self._execute_watch("file", watch)

        for watch in self.ping:
            self._execute_watch("ping", watch)

        table_header = []  # type: List[str]
        file_lines = [
            ("File", value[0], value[1]) for key, value in self.result["file"].items()
        ]
        ping_lines = [
            ("Ping", value[0], value[1]) for key, value in self.result["ping"].items()
        ]
        separator = [("--------", "------------------", "-------")]
        if file_lines and ping_lines:
            table_lines = file_lines + separator + ping_lines
        else:
            table_lines = file_lines or ping_lines
        table = tabulate(table_lines, table_header)
        self._widget = dashing.Text(
            table,
            color=6,
            border_color=5,
            background_color=self.background_color,
            title="Watchers",
        )

    @property
    def file(self) -> dict:
        """Return watchers for file dict.

        Default: {}

        :return: dict
        """
        return self._watchers.get("file_watch", {})

    @property
    def external(self) -> list:
        """Return watchers using external tools.

        Default: []

        :return: list
        """
        return self._watchers.get("external_tool", [])

    @property
    def ping(self) -> dict:
        """Return watchers for ping addresses.

        Default: {}

        :return: dict
        """
        return self._watchers.get("ping", {})

    def _execute_watch(self, watch_type: str, watch_name: str) -> None:
        """Execute data update for specific user watch type.

        :param watch_type: watch type (ping, external or file)

        :param watch_name: watch name

        :return:  None
        """
        watch_data = getattr(self, watch_type).get(watch_name)
        if not self.result[watch_type].get(watch_name):
            self.result[watch_type][watch_name] = [watch_data["name"], "Fetching..."]
        getattr(self, "_get_{}_result".format(watch_type))(watch_data, watch_name)

    def _get_ping_result(self, watch_data: dict, watch_name: str) -> None:
        """Get ping result for informed watch.

        :param watch_data: watch data

        :param watch_name: watch name

        :return: None
        """
        ret = run_command(
            "curl -f --connect-timeout {} {} 1>/dev/null 2>/dev/null".format(
                watch_data.get("timeout", 1), watch_data["address"]
            )
        )

        message_on_success = watch_data.get("message_on_success", "OK")
        message_on_error = watch_data.get("message_on_error", "ERROR")

        self.result["ping"][watch_name] = [
            formatStr.success(watch_data["name"], use_prefix=False)
            if ret
            else formatStr.error(watch_data["name"], use_prefix=False),
            formatStr.success(message_on_success, use_prefix=False)
            if ret
            else formatStr.error(message_on_error, use_prefix=False),
        ]

    def _get_file_result(self, watch_data: dict, watch_name: str) -> None:
        """Check file status based on watch data.

        :param watch_data: watch data

        :param watch_name: watch name

        :return: None
        """
        # Check destination git state
        dest_path = get_path(watch_data["dest_path"], self.config.base_path)
        dest_state = self.git.get_behind_state(dest_path)

        # Check source git state
        if watch_data.get("source_path"):
            source_path = get_path(watch_data["source_path"], self.config.base_path)
            source_state = self.git.get_behind_state(source_path)

            # Check timestamp between files
            source_name = (
                watch_data["source_name"]
                if watch_data.get("source_name")
                else watch_data["name"]
            )

            dest_full_path = os.path.join(dest_path, watch_data["name"])
            source_full_path = os.path.join(source_path, source_name)

            if not os.path.isfile(dest_full_path) or not os.path.isfile(
                source_full_path
            ):
                time_state = "NOT FOUND"
                style = "warning"
            else:
                source_date = os.path.getmtime(source_full_path)
                dest_date = os.path.getmtime(dest_full_path)

                if source_date > dest_date:
                    time_state = "NEED UPDATE"
                    style = "error"
                else:
                    time_state = "OK".ljust(5)
                    style = "success"

            # Save state in dictionary
            if "OK" not in source_state:
                name = format_color(watch_data["name"], style="error")
                self.result["file"][watch_name] = [name, source_state]
            elif "OK" not in dest_state:
                name = format_color(watch_data["name"], style="error")
                self.result["file"][watch_name] = [name, dest_state]
            else:
                name = format_color(watch_data["name"], style=style)
                self.result["file"][watch_name] = [name, time_state]


class SystemWatch(Watch):
    """System Watch class.

    Watch for system monitors (using psutil).
    """

    _interval = 0.25

    @staticmethod
    def _get_docker_folder_size() -> float:
        """Get total size occupied by docker data in bytes."""
        multiple = {"B": 1, "KB": 1024, "MB": 1024 * 1024, "GB": 1024 * 1024 * 1024}
        total_size = 0.0
        docker_sizes = run_command(
            "docker system df --format '{{.Size}}'", get_stdout=True
        )
        for line in docker_sizes.split("\n"):
            if not line:
                continue
            value = re.sub(r"[A-Za-z]+", "", line)
            size = re.sub(r"[0-9.]+", "", line)
            m = [multiple[key] for key in multiple if key.upper() == size.upper()][0]
            total_size += float(value) * m

        return total_size

    def _execute(self) -> None:
        """Get machine info using PSUtil."""
        cpu_percent = round(psutil.cpu_percent(interval=None) * 10, 0) / 10
        free_memory = int(psutil.virtual_memory().available / 1024 / 1024)
        total_memory = int(psutil.virtual_memory().total / 1024 / 1024)
        memory_percent = (free_memory / total_memory) * 100
        free_space = round(psutil.disk_usage("/").free / 1024 / 1024 / 1024, 1)
        total_space = round(psutil.disk_usage("/").total / 1024 / 1024 / 1024, 1)
        space_percent = (free_space / total_space) * 100
        docker_usage = round(self._get_docker_folder_size() / 1024 / 1024 / 1024, 1)
        docker_percentage = (docker_usage / (total_space - free_space)) * 100

        if memory_percent > 100:
            memory_percent = 100

        if space_percent > 100:
            space_percent = 100

        if docker_percentage > 100:
            docker_percentage = 100

        if cpu_percent <= 50:
            cpu_color = 2
        elif cpu_percent <= 70:
            cpu_color = 3
        else:
            cpu_color = 1

        if memory_percent <= 20:
            memory_color = 1
        elif memory_percent <= 50:
            memory_color = 3
        else:
            memory_color = 2

        if space_percent <= 20:
            space_color = 1
        elif space_percent <= 50:
            space_color = 3
        else:
            space_color = 2

        if docker_percentage <= 33:
            docker_color = 2
        else:
            docker_color = 3

        self._widget = dashing.VSplit(
            dashing.HSplit(
                dashing.HGauge(
                    val=cpu_percent,
                    color=cpu_color,
                    border_color=cpu_color,
                    title="CPU:{}%".format(cpu_percent),
                    background_color=self.background_color,
                ),
                dashing.HGauge(
                    val=memory_percent,
                    color=memory_color,
                    border_color=memory_color,
                    title="Free Mem:{}M".format(free_memory),
                    background_color=self.background_color,
                ),
                dashing.HGauge(
                    val=space_percent,
                    color=space_color,
                    border_color=space_color,
                    title="Free Space:{}Gb".format(free_space),
                    background_color=self.background_color,
                ),
            ),
            dashing.HGauge(
                val=docker_percentage,
                color=docker_color,
                border_color=docker_color,
                title="Docker Used Space:{}Gb of {}Gb used".format(
                    docker_usage, round(total_space - free_space, 1)
                ),
                background_color=self.background_color,
            ),
        )
