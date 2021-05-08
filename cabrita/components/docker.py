"""
Docker module.

This module contains the DockerInspect class
which is responsible to inspect docker data from
each service in dashboard.
"""
import datetime
import json
import os
import time
from collections import Counter
from enum import Enum
from typing import List, Optional, Tuple, Union

from tzlocal import get_localzone

from cabrita.abc.base import InspectTemplate
from cabrita.abc.utils import get_path, persist_on_disk
from cabrita.components.config import Compose

IN = "↗"
OUT = "↘"
BOTH = "⇄"


class PortDetail(Enum):
    """Port Detail for docker ports.

    Ports are determined by the 'ports' and 'expose'
    parameters inside docker-compose.yml files.

    Options
    -------
        * **external**: show external ports only
        * **internal**: show internal ports only
        * **both**: show both ports.
    """

    external = "external"
    internal = "internal"
    both = "both"


class PortView(Enum):
    """Port View for docker ports.

    Defines where to show port information on box.

    Options:
        * **hidden**: Do not show info.
        * **column**: Show ports info in a separate column
        * **name**: Show ports info after service name
        * **status**: Show ports info after service status
    """

    hidden = "hidden"
    column = "column"
    name = "name"
    status = "status"


class DockerInspect(InspectTemplate):
    """DockerInspect class."""

    def __init__(
        self,
        compose: Compose,
        interval: int,
        port_view: PortView,
        port_detail: PortDetail,
        files_to_watch: List[str],
        services_to_check_git: List[str],
    ) -> None:
        """Init class."""
        super(DockerInspect, self).__init__(compose, interval)
        self.port_view = PortView(port_view)
        self.port_detail = PortDetail(port_detail)
        self.files_to_watch = files_to_watch
        self.services_to_check_git = services_to_check_git
        self.default_data = {
            "name": "Fetching...",
            "status": "Fetching...",
            "format": "dark",
            "ports": "",
        }

    def inspect(self, service: str) -> None:
        """Inspect docker container.

        :param service: service name as defined in docker-compose yml.

        :return: None
        """
        index = 1
        all_containers_processed = False
        result_list = []  # type: list
        need_build = False
        while not all_containers_processed:
            container_name = self._get_container_name(service, index)
            inspect_data = self._get_inspect_data(container_name)

            if not inspect_data:
                if not result_list:
                    result_list.append(("Not Found", "info", "dark"))
                all_containers_processed = True
            elif self._need_build(service, inspect_data):
                need_build = True
                result_list.append(("NEED BUILD", "error", None))
                index += 1
            else:
                result_list.append(self._define_status(inspect_data))
                index += 1

        if need_build:
            persist_on_disk("add", service, "need_image")
        else:
            persist_on_disk("remove", service, "need_image")

        if len(result_list) == 1:
            service_status = result_list[0][0]
            text_style = result_list[0][1]
            text_theme = result_list[0][2]
        elif need_build:
            service_status = "NEED BUILD"
            text_style = "error"
            text_theme = None
        else:
            stats = Counter([result[0] for result in result_list]).most_common()[0][0]
            service_status = "{}{}".format(
                stats,
                " x{}".format(len(result_list))
                if "exited" not in stats.lower()
                else "",
            )
            text_style = Counter([result[1] for result in result_list]).most_common()[
                0
            ][0]
            text_theme = Counter([result[2] for result in result_list]).most_common()[
                0
            ][0]

        self._status[service] = {
            "name": service,
            "status": service_status,
            "style": text_style,
            "theme": text_theme,
            "ports": self._get_service_ports(service),
        }

    def _get_service_ports(self, service: str) -> str:
        """Get docker services port info.

        Will format text according the 'port_view' and 'port_detail' options.

        :param service: service name as defined in docker-compose yml.

        :return: string
        """
        internal_ports = []
        external_ports = []
        port_list = self.compose.get_ports_from_service(service) or ""

        if not port_list:
            return ""

        for port in port_list:
            if ":" in port:
                external_ports.append("{}".format(port.split(":")[0]))
                internal_ports.append("{}".format(port.split(":")[-1]))
            else:
                internal_ports.append("{}".format(port))

        external_ports = sorted(set(external_ports))
        internal_ports = sorted(set(internal_ports))

        if internal_ports == external_ports:
            return "{} {}".format(BOTH, " ".join(external_ports))

        if self.port_detail == PortDetail.external:
            service_string = "{} {}".format(OUT, "/".join(external_ports))
        elif self.port_detail == PortDetail.internal:
            service_string = "{} {}".format(IN, "/".join(internal_ports))
        else:
            service_string = "{} {} {} {}".format(
                OUT, "/".join(external_ports), IN, "/".join(internal_ports)
            )

        return service_string

    def _get_container_name(self, service: str, index: int = 1) -> str:
        """Return container name for informed service.

        Name can be retrieved from 'container_name' parameter in
        docker-compose.yml files or calculated using this mask:
        ``<folder_name>_<service_name>_1``

        :param service: service name as defined in docker-compose yml.

        :return: string
        """
        # Try container_name first
        name = self.compose.get_from_service(service, "container_name")
        if not name:
            # Generate default_name
            name = os.path.basename(os.path.dirname(self.compose.full_path))
            name = "{}_{}_{}".format(name.lower(), service.lower(), index)
        return name

    def _get_inspect_data(self, service: str) -> dict:
        """Run docker inspect command.

        :param service: service name as defined in docker-compose yml.

        :return: dict
        """
        ret = self.run("docker inspect {} 2>/dev/null".format(service), get_stdout=True)
        return json.loads(ret)[0] if ret else {}

    @staticmethod
    def _get_running_status(inspect_state: dict) -> str:
        """Get running status from inspect data.

        :param inspect_state: dict from 'State' key in docker inspect data

        :return: string
        """
        if (
            inspect_state.get("Health", False)
            and inspect_state["Status"].lower() == "running"
        ):
            service_status = inspect_state["Health"]["Status"].title()
        else:
            service_status = inspect_state["Status"].title()
        return service_status

    @staticmethod
    def _get_style_and_theme_for_status(
        status: str, inspect_state: dict
    ) -> Tuple[str, Union[str, None]]:
        """Get text theme and style for status.

        :param status: status retrieved from docker inspect data

        :param inspect_state: dict from 'State' key in docker inspect data

        :return: tuple (string, string or None)
        """
        if not inspect_state["Running"] and not inspect_state["Paused"]:
            return "info", "dark"
        if status.lower() in ["running", "healthy"]:
            return "success", None
        if inspect_state["Health"]["FailingStreak"] > 3:
            return "error", None
        else:
            return "warning", None

    def _define_status(self, inspect_data) -> Tuple[str, str, Optional[str]]:
        """Return service running status based on docker inspect data.

        :param inspect_data: docker inspect data.

        :return: tuple (string, string, string or None)
        """
        if not inspect_data.get("State"):
            return "Error", "error", None
        status = self._get_running_status(inspect_data["State"])
        style, theme = self._get_style_and_theme_for_status(
            status, inspect_data["State"]
        )

        return status, style, theme

    def _need_build(self, service: str, inspect_data: dict) -> bool:
        """Check if service need build.

        This check use the following parameters from yml file:

        **watch_for_build_using_files**

            Will check if any of the files listed in this parameter have
            his modification date more recent than service docker image build date.

        **watch_for_build_using_git**

            Will check if any of the services listed in this parameters have
            his last commit data more recent than service docker image build date.

        :param service: service name as defined in docker-compose yml.

        :param inspect_data: docker inspect data.

        :return: bool
        """
        test_date = None
        image_name = inspect_data["Config"]["Image"]
        image_data = self.run(
            "docker inspect {} 2>/dev/null".format(image_name), get_stdout=True
        )
        if image_data:
            image_data = json.loads(image_data)[0]

            # Get current UTC offset
            time_now = datetime.datetime.now()
            time_now_utc = datetime.datetime.utcnow()
            time_offset_seconds = (time_now - time_now_utc).total_seconds()
            utc_offset = time.gmtime(abs(time_offset_seconds))
            utc_string = "{}{}".format(
                "-" if time_offset_seconds < 0 else "+",
                time.strftime("%H%M", utc_offset),
            )
            date = image_data.get("Created")[:-4] + " " + utc_string
            test_date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f %z")

        label = inspect_data["Config"]["Labels"].get("com.docker.compose.service")
        if not label:
            return False
        full_path = None
        if test_date and self.compose.get_from_service(label, "build"):
            build_path = self.compose.get_from_service(label, "build")
            if isinstance(build_path, dict):
                build_path = build_path.get("context")
            full_path = get_path(build_path, self.compose.base_path)
            list_dates = [
                datetime.datetime.fromtimestamp(
                    os.path.getmtime(os.path.join(full_path, file)), tz=get_localzone()
                )
                for file in self.files_to_watch
                if os.path.isfile(os.path.join(full_path, file))
            ]
            if list_dates:
                if max(list_dates) > test_date:
                    return True

        # Check for build using commit
        # Ex.: 2018-02-23 18:31:45 -0300
        if service in self.services_to_check_git and full_path:
            git_log = self.run(
                'cd {} && git log -1 --pretty=format:"%cd" --date=iso'.format(
                    full_path
                ),
                get_stdout=True,
            )
            date_fmt = "%Y-%m-%d %H:%M:%S %z"
            if git_log:
                commit_date = datetime.datetime.strptime(git_log, date_fmt)
                if commit_date > test_date:
                    return True

        return False
