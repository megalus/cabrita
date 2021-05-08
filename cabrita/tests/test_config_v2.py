import os
from pathlib import Path
from unittest import TestCase

from cabrita.components.config import Config
from cabrita.tests import LATEST_CONFIG_PATH


class TestConfig(TestCase):
    def setUp(self):
        self.maxDiff = None
        self._generate_config()

    def _generate_config(self):
        self.config = Config()
        self.config.add_path(LATEST_CONFIG_PATH)
        self.config.load_file_data()
        self.assertTrue(self.config.is_valid)

    def test_ignore_services(self):
        self.assertEqual(self.config.ignore_services, ["portainer"])

    def test_compose_files(self):
        self.assertEqual(
            self.config.compose_files,
            [
                "$TEST_PROJECT_PATH/docker-compose.yml",
                "$TEST_PROJECT_PATH/docker-compose.override.yml",
            ],
        )

    def test_layout(self):
        self.assertEqual(self.config.layout, "horizontal")

    def test_boxes(self):
        self.assertEqual(len(self.config.boxes.keys()), 3)
        for box_name in self.config.boxes.keys():
            self.assertTrue(box_name in ["all", "workers", "devops"])

    def test_title(self):
        self.assertEqual(self.config.title, "My Docker Project")

    def test_background_color(self):
        from cabrita.components import BoxColor

        self.assertEqual(self.config.background_color, BoxColor.grey)

    def test_background_color_value(self):
        self.assertEqual(self.config.background_color_value, 0)

    def test_watchers(self):
        pass

    def test_get_compose_path(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = str(Path(current_dir).parent.parent)
        os.environ["TEST_PROJECT_PATH"] = os.path.join(parent_dir, "examples")
        self.assertEqual(
            Path(
                self.config.get_compose_path(
                    "$TEST_PROJECT_PATH/docker-compose.yml", parent_dir
                )
            ),
            Path(os.path.join(parent_dir, "examples/docker-compose.yml")).resolve(),
        )

    def test_generate_boxes(self):
        services_list = {"django": {}, "django-worker": {}, "flask": {}}
        expected_box = {
            "box_0": {
                "includes": ["django", "django-worker", "flask"],
                "name": "Docker Services",
                "port_view": "column",
                "show_revision": True,
                "size": "small",
            }
        }
        self.config.generate_boxes(services_list)
        self.assertListEqual(
            self.config.boxes["box_0"]["includes"], expected_box["box_0"]["includes"]
        )
        self.assertEqual(
            self.config.boxes["box_0"]["name"], expected_box["box_0"]["name"]
        )
        self.assertEqual(
            self.config.boxes["box_0"]["port_view"], expected_box["box_0"]["port_view"]
        )
        self.assertEqual(
            self.config.boxes["box_0"]["show_revision"],
            expected_box["box_0"]["show_revision"],
        )
        self.assertEqual(
            self.config.boxes["box_0"]["size"], expected_box["box_0"]["size"]
        )

    def test_bad_config(self):
        self.config = Config()
        self.config.add_path("./examples/config/cabrita-v2.yml")
        self.config.load_file_data()
        self.config.data["layout"] = "triangular"
        self.config.data["background_color"] = "no_color"
        self.config.data["compose_files"] = {}
        self.config.data["boxes"] = {
            "wrong_box": {
                "size": "ultra_large",
                "port_view": "wrong_option",
                "port_detail": "wrong_option",
                "watch_for_build_using_files": {},
                "watch_for_build_using_git": {},
                "includes": {},
                "categories": {},
            }
        }
        self.config.data["ignore_services"] = {}
        self.assertFalse(self.config.is_valid)
