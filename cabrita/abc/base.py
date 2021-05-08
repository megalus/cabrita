"""Base Module.

ConfigTemplate
^^^^^^^^^^^^^^

Base class for the config template object.
This template will process the YAML files.
Subclasses are: Config and Compose classes

InspectTemplate
^^^^^^^^^^^^^^^

Base class for the Inspector template object.
This template will process docker and git status for compose services
Subclasses are: DockerInspect and GitInspect

"""
import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

import yaml
from buzio import console

from cabrita.abc.utils import get_path, run_command


class ConfigTemplate(ABC):
    """Abstract class for processing yaml files."""

    def __init__(self) -> None:
        """Initialize class.

        :param
            compose_data_list: data parsed for each yaml
        :param
            _base_path: base path based on config file
        :param
            list_path: path list for each yaml
        :param
            full_path: full resolved path list for each yaml
        :param
            data: dictionary for resolved data from all yamls
        :param
            console: buzio instance
        :param
            manual_compose_paths: list of docker-compose paths informed on prompt
        """
        self.compose_data_list = []  # type: List[dict]
        self._base_path = ""
        self.list_path = []  # type: List[Tuple[str, str]]
        self.full_path = ""  # type: str
        self.data = {}  # type: Dict[str, Any]
        self.console = console
        self.manual_compose_paths = []  # type: List[dict]

    @property
    def base_path(self) -> str:
        """Return base path for yaml file."""
        return self._base_path

    @base_path.setter
    def base_path(self, value):
        self._base_path = value if "$" not in value else get_path(value, "")

    @property
    def version(self) -> int:
        """Return version value inside yaml file."""
        return int(self.data.get("version", 0))

    @property
    @abstractmethod
    def is_valid(self) -> bool:
        """Check if yaml is valid."""
        pass

    def add_path(self, path: str, base_path: str = os.getcwd()) -> None:
        """Add new path for list for each yaml file."""
        if path:
            if not self.base_path:
                self.base_path = os.path.dirname(os.path.join(base_path, path))
            self.list_path.append((path, base_path))

    def load_file_data(self) -> None:
        """Load data from yaml file.

        First file will be the main file.
        Every other file will override data, on reversed order list:

        Example:
            1. docker-compose.yml (main file)
            2. docker-compose-dev.yml (override main)
            3. docker-compose-pycharm.yml (override dev)
        """
        if self.list_path:
            for path, base_path in self.list_path:
                try:
                    self.full_path = get_path(path, base_path)
                    self.console.info("Reading {}".format(self.full_path))
                    with open(self.full_path, "r") as file:
                        self.compose_data = yaml.safe_load(file.read())
                        for key in self.compose_data:  # type: ignore
                            self._convert_lists(self.compose_data, key)
                        self.compose_data_list.append(self.compose_data)
                except FileNotFoundError as exc:
                    console.error("Cannot open file: {}".format(exc))
                    sys.exit(127)
                except yaml.YAMLError as exc:
                    console.error("Cannot read file: {}".format(exc))
                    sys.exit(1)
                except Exception as exc:
                    console.error("Error: {}".format(exc))
                    raise exc
            self._upload_compose_list()

    def _convert_lists(self, data, key):
        """Convert list to dict inside yaml data.

        Works only for Key=Value lists.

        Example:
            environment:
                - DEBUG=false
            ports:
                - "8090:8080"

        Result:
            environment: {"DEBUG": "false"}
            ports: ['8090:8080']

        """
        if isinstance(data[key], list) and "=" in data[key][0]:
            data[key] = {obj.split("=")[0]: obj.split("=")[-1] for obj in data[key]}
        if isinstance(data[key], dict):
            for k in data[key]:
                self._convert_lists(data[key], k)

    def _upload_compose_list(self):
        """Reverse yaml list order and override data."""
        reversed_list = list(reversed(self.compose_data_list))
        self.data = reversed_list[-1]
        for index, override in enumerate(reversed_list):
            self.override = override
            if index + 1 == len(reversed_list):
                break
            for key in self.override:
                self._load_data_from_override(self.override, self.data, key)

    def _load_data_from_override(self, source, target, key):
        """Append override data in self.compose.

        Example Compose::
        ---------------
        core:
            build:
                context: ../core
            image: core
            networks:
                - backend
            environment:
                - DEBUG=false
            ports:
             - "8080:80"

        Example override::
        ----------------
        core:
            build:
                dockerfile: Docker_dev
            depends_on:
                - api
            command: bash -c "python manage.py runserver 0.0.0.0"
            environment:
                DEBUG: "True"
            ports:
                - "9000:80"

        Final Result::
        ------------
        core:
            build:
                context: ../core
                dockerfile: Docker_dev
            depends_on:
                - api
            image: core
            command: bash -c "python manage.py runserver 0.0.0.0"
            environment:
                DEBUG: "True"
            networks:
                - backend
            ports:
             - "8080:80"
             - "9000:80"

        """
        if target.get(key, None):
            if isinstance(source[key], dict):
                for k in source[key]:
                    self._load_data_from_override(
                        source=source[key], target=target[key], key=k
                    )
            else:
                if isinstance(target[key], list) and isinstance(source[key], list):
                    target[key] += source[key]
                else:
                    target[key] = source[key]
        else:
            if isinstance(target, list) and isinstance(source[key], list):
                target[key] += source[key]
            else:
                target[key] = source[key]


class InspectTemplate(ABC):
    """Abstract class for compose service inspectors."""

    def __init__(self, compose, interval: int) -> None:
        """Initialize class.

        :param
            run: running commands code.
        :param
            compose: Compose instance.
        :param
            _status: service status based on inspect data.
        :param
            interval: interval in seconds for new inspection
        :param
            last_update: last update for the inspector
        :param
            default_data: pydashing default widget

        """
        self.run = run_command
        self.compose = compose
        self._status = {}  # type: dict
        self.interval = interval
        self.last_update = datetime.now() - timedelta(seconds=self.interval)
        self.default_data = {}  # type: dict

    @abstractmethod
    def inspect(self, service: str) -> None:
        """Run inspect code."""
        pass

    @property
    def can_update(self) -> bool:
        """Check if inspector can inspect again."""
        seconds_elapsed = (datetime.now() - self.last_update).total_seconds()
        return seconds_elapsed >= self.interval

    def status(self, service):
        """Return service status.

        If can update, start fetching new data calling self.inspect method.

        :param service:
            docker service name
        :return:
            dict or dashing obj. If not fetch data yet send default widget.
        """
        if self.can_update:
            self.inspect(service)

        return self._status.get(service, self.default_data)
