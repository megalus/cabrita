import os
from pathlib import Path
from unittest import TestCase

from cabrita.components.config import Config


class TestConfig(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.manual_files = [
            "./examples/docker-compose.yml",
            "./examples/docker-compose.override.yml",
        ]
        self._generate_config()

    def _generate_config(self):
        self.config = Config()
        self.config.manual_compose_paths = self.manual_files
        self.config.load_file_data()
        self.assertTrue(self.config.is_valid)

    def test_ignore_services(self):
        self.assertEqual(self.config.ignore_services, [])

    def test_compose_files(self):
        self.assertEqual(self.config.compose_files, self.manual_files)

    def test_layout(self):
        self.assertEqual(self.config.layout, "horizontal")

    def test_title(self):
        self.assertEqual(self.config.title, "Docker-Compose")

    def test_background_color(self):
        from cabrita.components import BoxColor

        self.assertEqual(self.config.background_color, BoxColor.black)

    def test_background_color_value(self):
        self.assertEqual(self.config.background_color_value, 16)

    def test_get_compose_path(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = Path(current_dir).parent.parent
        self.assertEqual(
            Path(self.config.get_compose_path(self.manual_files[0], str(parent_dir))),
            Path(os.path.join(str(parent_dir), self.manual_files[0])).resolve(),
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
