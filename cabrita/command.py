"""
Command module.

This module has the CabritaCommand class, which is responsible for:

1. Load and check for valid cabrita.yml file
2. Load and check for valid docker-compose.yml files
3. Generate and add docker services to boxes
4. Generate and add watchers to dashboard
"""
import os
import sys
from typing import List, Optional

from cabrita.components import BoxColor
from cabrita.components.box import Box
from cabrita.components.config import Compose, Config
from cabrita.components.dashboard import Dashboard
from cabrita.components.docker import DockerInspect, PortDetail, PortView
from cabrita.components.git import GitInspect
from cabrita.components.watchers import DockerComposeWatch, SystemWatch, UserWatch


class CabritaCommand:
    """Cabrita Command class."""

    def __init__(
        self,
        cabrita_path: str,
        compose_path: tuple,
        background_color: Optional[str] = "black",
        version: str = "dev",
    ) -> None:
        """Init class."""
        self.version = version
        self.cabrita_path = cabrita_path
        self.config = Config()
        self.config.add_path(self.cabrita_path)
        self.config.load_file_data()
        self.config.manual_compose_paths = list(compose_path)
        self.compose = None  # type: Compose
        self.dashboard = None  # type: Dashboard
        self._background_color = background_color

    @property
    def background_color(self):
        """Return Background Color enum.

        :return: BoxColor instance
        """
        return (
            getattr(BoxColor, self._background_color)
            if self._background_color
            else self.config.background_color
        )

    @property
    def has_a_valid_config(self) -> bool:
        """Return if Config data is valid.

        :return: bool
        """
        return self.config.is_valid

    @property
    def has_a_valid_compose(self) -> bool:
        """Return if Compose data is valid.

        :return: bool
        """
        return self.compose.is_valid

    def read_compose_files(self) -> None:
        """Read docker compose files data.

        :return: None
        """
        self.compose = Compose()
        for compose in self.config.compose_files:
            base_compose_path = os.path.dirname(compose)
            if "." in base_compose_path:
                base_compose_path = self.config.base_path
            self.compose.add_path(compose, base_path=base_compose_path)
            if not self.compose.is_valid:
                sys.exit(1)
        self.compose.load_file_data()
        if self.config.version == 0:
            self.config.generate_boxes(self.compose.services)

    def _add_watchers(self) -> None:
        """Configure and add watchers to dashboard.

        :return: None
        """
        git = GitInspect(target_branch="", interval=30, compose=self.compose)
        self.dashboard.compose_watch = DockerComposeWatch(
            background_color=self.background_color,
            git=git,
            config=self.config,
            version=self.version,
        )
        self.dashboard.system_watch = SystemWatch(
            background_color=self.background_color
        )
        self.dashboard.user_watches = UserWatch(
            background_color=self.background_color, git=git, config=self.config
        )

    def _add_services_in_boxes(self) -> None:
        """Configure and add docker services to dashboard boxes.

        The 'main' box are the last to be processed, because this
        box will include any non-ignored service which aren't
        included in any box before.

        :return: None
        """
        included_services = []  # type: List[str]
        main_box = None

        for name in self.config.boxes:
            box_data = self.config.boxes[name]
            docker = DockerInspect(
                compose=self.compose,
                interval=box_data.get("interval", 0),
                port_view=box_data.get("port_view", PortView.hidden),
                port_detail=box_data.get("port_detail", PortDetail.external),
                files_to_watch=box_data.get("watch_for_build_using_files", []),
                services_to_check_git=box_data.get("watch_for_build_using_git", []),
            )
            git = GitInspect(
                target_branch=box_data.get("watch_branch", ""),
                interval=box_data.get("git_fetch_interval", 30),
                compose=self.compose,
            )

            services_in_box = []
            for service in self.compose.services:
                if (
                    service not in included_services
                    and service not in self.config.ignore_services
                ):
                    services_list = set(
                        [
                            s.lower()
                            for s in box_data.get("includes", [])
                            + box_data.get("categories", [])
                        ]
                    )
                    for service_name in services_list:
                        if service_name.lower() in service.lower():
                            services_in_box.append(service)
                            included_services.append(service)

            box = Box(
                compose=self.compose,
                docker=docker,
                git=git,
                background_color=self.background_color,
            )
            box.services = services_in_box
            box.load_data(box_data)

            if box.main:
                main_box = box
            else:
                self.dashboard.add_box(box)
        if main_box:
            for service in self.compose.services:
                if (
                    service not in included_services
                    and service not in self.config.ignore_services
                ):
                    main_box.add_service(service)
            self.dashboard.add_box(main_box)

    def prepare_dashboard(self) -> None:
        """Prepare the dashboard.

        :return: None
        """
        self.dashboard = Dashboard(config=self.config)
        self._add_watchers()
        self._add_services_in_boxes()

    def execute(self) -> None:
        """Execute dashboard to show data in terminal.

        :return: None
        """
        self.dashboard.run()
