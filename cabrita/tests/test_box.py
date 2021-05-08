from __future__ import unicode_literals

from unittest import TestCase, mock

import yaml
from dashing import dashing

from cabrita.components import BoxColor
from cabrita.components.box import Box, update_box
from cabrita.components.docker import PortView


class TestBox(TestCase):
    def return_docker_status(self, service):
        mock_dict = {
            "django": {
                "ports": "↘ 8081",
                "status": "Running",
                "name": "django",
                "style": "success",
                "theme": None,
            },
            "django-worker": {
                "ports": "↘ 8085",
                "status": "Running",
                "name": "django-worker",
                "style": "success",
                "theme": None,
            },
        }
        return mock_dict[service]

    def return_revision_status(self, service):
        mock_dict = {"django": "✎ 1.0.0@⑂ abcd12345", "django-worker": "Using Image"}
        return mock_dict[service]

    def return_git_status(self, service):
        mock_dict = {"django": "master ↓ 1", "django-worker": "Using Image"}
        return mock_dict[service]

    @mock.patch("cabrita.components.config.Compose")
    @mock.patch("cabrita.components.git.GitInspect")
    @mock.patch("cabrita.components.docker.DockerInspect")
    def setUp(self, *args):
        compose_mock = args[2]
        with open("./examples/docker-compose.yml") as file:
            compose_data = yaml.load(file.read())
        compose_mock.services = compose_data["services"]

        docker_mock = args[0]
        docker_mock.status = self.return_docker_status

        git_mock = args[1]
        git_mock.get_git_revision = self.return_revision_status
        git_mock.status = self.return_git_status

        self.box = Box(
            compose=compose_mock,
            git=git_mock,
            docker=docker_mock,
            background_color=BoxColor.black,
        )
        self.box.load_data(
            {
                "show_revision": True,
                "port_view": PortView.column,
                "categories": ["worker"],
                "includes": ["django"],
            }
        )
        self.box.services = ["django", "django-worker"]

    def test_can_update(self):
        assert self.box.can_update is False

    def test_widget(self):
        assert isinstance(self.box.widget, dashing.Text)

    def test_interval(self):
        assert self.box.interval != 0

    def test_show_git(self):
        assert isinstance(self.box.show_git, bool)
        assert self.box.show_git is True

    def test_show_revision(self):
        assert isinstance(self.box.show_revision, bool)
        assert self.box.show_revision is True

    def test_port_view(self):
        from cabrita.components.docker import PortView

        assert self.box.port_view is PortView.column

    def test_port_detail(self):
        from cabrita.components.docker import PortDetail

        assert self.box.port_detail is PortDetail.external

    def test_categories(self):
        assert isinstance(self.box.categories, list)

    def test_title(self):
        assert self.box.title == "Box"

    def test_size(self):
        assert self.box.size == "large"

    def test_main(self):
        assert self.box.main is not True
        assert isinstance(self.box.main, bool)

    def test_includes(self):
        assert isinstance(self.box.categories, list)

    def test_background_color(self):
        assert self.box.background_color == BoxColor.black.value

    def test_load_data(self):
        assert self.box.show_revision is True

    def test_add_service(self):
        self.box.add_service("pyramid")
        assert len(self.box.services) == 3

    def test__get_headers(self):
        test_headers = self.box._get_headers()
        self.assertListEqual(
            test_headers, ["Service", "Status", "Commit", "Port", "Branch", "Worker"]
        )

    def test__append_ports_in_field(self):
        self.box.run()
        self.box.data["port_view"] = PortView.name
        test_name = self.box._append_ports_in_field("name")
        test_status = self.box._append_ports_in_field("status")
        self.assertEqual(test_name, "django (↘ 8081)")
        self.assertEqual(test_status, "Running")

        self.box.data["port_view"] = PortView.status
        test_name = self.box._append_ports_in_field("name")
        test_status = self.box._append_ports_in_field("status")
        self.assertEqual(test_name, "django")
        self.assertEqual(test_status, "Running (↘ 8081)")

    def test_run(self):
        test_result = (
            "Service    Status    Commit               Port    Branch      Worker\n"
            "---------  --------  -------------------  ------  ----------  --------\n"
            "[32mdjango[22m     [32mRunning[22m   [36m✎ 1.0.0 [22m[37m"
            "[2m⑂ abcd12345[22m  [32m↘ 8081[22m  master ↓ 1  [32mRunning[22m"
        )

        self.box.run()
        self.assertEqual(self.box.widget.text, test_result)

    def test__get_service_category_data(self):
        self.box.run()
        ret = self.box._get_service_category_data("django", "worker")
        self.assertIsNone(ret)
        self.box._included_service_list = []
        ret = self.box._get_service_category_data("django", "worker")
        self.assertEqual(ret, self.return_docker_status("django-worker"))

    def test_format_revision(self):
        self.box.run()
        revision_data = self.return_revision_status("django")
        table_lines = [
            ["django", "running", revision_data],
            ["dummy", "running", "✎ very_long_tag_line@⑂ abcd12345"],
        ]
        test_data = self.box.format_revision(table_lines)
        self.assertEqual(
            test_data[0][-1], "[36m✎ 1.0.0              [22m[37m[2m⑂ abcd12345[22m"
        )

    def test_update_box(self, *args):
        ret = update_box(self.box)
        self.assertIsInstance(ret, dashing.Text)
