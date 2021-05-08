import json
from unittest import TestCase, mock

from cabrita.command import CabritaCommand
from cabrita.tests import (
    INSPECT_DJANGO_CONTAINER,
    INSPECT_DJANGO_IMAGE,
    LATEST_CONFIG_PATH,
)


def return_run_data(*args, **kwargs):
    command = args[0]
    if "inspect" in command:
        return INSPECT_DJANGO_IMAGE
    if "log" in command:
        return "2018-05-17 11:03:46 -0300"
    return False


class TestDockerInspect(TestCase):
    @classmethod
    def setUpClass(cls):
        command = CabritaCommand(
            cabrita_path=LATEST_CONFIG_PATH, compose_path=(), version="test"
        )
        command.read_compose_files()
        command.prepare_dashboard()
        cls.docker = command.dashboard.all_boxes[3].docker

    @mock.patch("cabrita.components.docker.persist_on_disk")
    def test_inspect(self, *mocks):
        def _return_inspect_data(*args, **kwargs):
            if "examples_django_1" in args[0]:
                return INSPECT_DJANGO_CONTAINER
            else:
                return None

        result_dict = {
            "name": "django",
            "ports": "↘ 8081/8090",
            "status": "Running",
            "style": "success",
            "theme": None,
        }
        self.docker.run = _return_inspect_data
        self.docker.inspect("django")
        self.assertDictEqual(self.docker.status("django"), result_dict)

    def test__get_service_ports(self):
        test_ports = self.docker._get_service_ports("django")
        self.assertEqual(test_ports, "↘ 8081/8090")

    def test__get_container_name(self):
        test_name = self.docker._get_container_name("django")
        self.assertEqual(test_name, "examples_django_1")

    @mock.patch("cabrita.abc.utils.run_command", return_value=INSPECT_DJANGO_CONTAINER)
    def test__get_inspect_data(self, *mocks):
        test_name = self.docker._get_container_name("django")
        self.docker.run = mocks[0]
        test_data = self.docker._get_inspect_data(test_name)
        self.assertEqual(test_data, json.loads(INSPECT_DJANGO_CONTAINER)[0])

    @mock.patch("cabrita.abc.utils.run_command", return_value=INSPECT_DJANGO_CONTAINER)
    def test__define_status(self, *mocks):
        test_name = self.docker._get_container_name("django")
        self.docker.run = mocks[0]
        test_data = self.docker._get_inspect_data(test_name)
        test_stats, test_style, test_theme = self.docker._define_status(test_data)
        self.assertEqual(test_stats, "Running")
        self.assertEqual(test_style, "success")
        self.assertEqual(test_theme, None)

    @mock.patch("cabrita.abc.utils.run_command", return_value=INSPECT_DJANGO_CONTAINER)
    @mock.patch("cabrita.abc.utils.run_command", return_value=INSPECT_DJANGO_IMAGE)
    def test__need_build_using_files(self, image_mock, container_mock):
        service_name = "django"
        test_name = self.docker._get_container_name(service_name)
        self.docker.run = container_mock
        test_data = self.docker._get_inspect_data(test_name)
        self.docker.run = image_mock
        self.assertFalse(self.docker._need_build(service_name, test_data))

    @mock.patch("cabrita.abc.utils.run_command", return_value=INSPECT_DJANGO_CONTAINER)
    @mock.patch("cabrita.abc.utils.run_command", side_effect=return_run_data)
    def test__need_build_using_git(self, run_mock, container_mock):
        service_name = "flask"
        test_name = self.docker._get_container_name(service_name)
        self.docker.run = container_mock
        test_data = self.docker._get_inspect_data(test_name)
        self.docker.run = run_mock
        self.assertTrue(self.docker._need_build(service_name, test_data))
