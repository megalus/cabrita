import os
from pathlib import Path
from unittest import TestCase

from cabrita.components.config import Compose


class TestCompose(TestCase):
    def setUp(self):
        self.maxDiff = None
        self._generate_compose()

    def _generate_compose(self):
        self.compose = Compose()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = str(Path(current_dir).parent)
        self.compose.base_path = os.path.join(parent_dir, "examples")
        self.compose.add_path("./examples/docker-compose.yml")
        self.compose.add_path("./examples/docker-compose.override.yml")
        self.compose.load_file_data()
        result_dict = {
            "version": "3",
            "services": {
                "django": {
                    "build": {
                        "context": "./django_app",
                        "dockerfile": "Dockerfile_dev",
                    },
                    "image": "django:dev",
                    "ports": ["8081:8080", "8090:8080"],
                    "depends_on": ["postgres", "django-redis"],
                    "command": "python manage.py runserver 0.0.0.0:8080",
                    "environment": {"DEBUG": "True"},
                    "networks": {"backend": {"aliases": ["django"]}},
                    "volumes": ["./django_app:/opt/app"],
                    "healthcheck": {
                        "test": ["CMD", "curl", "-f", "http://localhost:8080"],
                        "interval": "30s",
                        "timeout": "5s",
                        "retries": 3,
                    },
                },
                "django-worker": {
                    "image": "django:dev",
                    "deploy": {"mode": "replicated", "replicas": 3},
                    "depends_on": ["django", "django-redis", "postgres"],
                    "volumes": ["${TEST_PROJECT_PATH}/django_app:/opt/app"],
                    "command": "celery -A django_app -b "
                    "redis://redis:6379 worker -l info",
                    "networks": {"backend": {"aliases": ["django-worker"]}},
                },
                "flask": {
                    "build": {"context": "./flask_app"},
                    "image": "flask:dev",
                    "ports": ["5010:5000"],
                    "depends_on": ["postgres"],
                    "volumes": ["./flask_app:/opt/app"],
                    "networks": {"backend": {"aliases": ["flask"]}},
                    "environment": {"FLASK_APP": "app.py", "FLASK_ENV": "development"},
                    "healthcheck": {
                        "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                        "interval": "30s",
                        "timeout": "5s",
                        "retries": 3,
                    },
                },
                "portainer": {
                    "image": "portainer/portainer",
                    "ports": ["9100:9000"],
                    "volumes": ["/var/run/docker.sock:/var/run/docker.sock"],
                    "networks": {"backend": {"aliases": ["portainer"]}},
                },
                "django-redis": {
                    "image": "redis:latest",
                    "ports": ["6380:6379"],
                    "networks": {"backend": {"aliases": ["redis"]}},
                },
                "postgres": {
                    "image": "postgres:9.6",
                    "volumes": ["postgres-app-data:/var/lib/postgresql/data"],
                    "ports": ["5433:5432"],
                    "networks": {"backend": {"aliases": ["postgres"]}},
                },
            },
            "networks": {"backend": {"driver": "bridge"}},
            "volumes": {"postgres-app-data": None},
        }
        self.assertDictEqual(self.compose.data, result_dict)

    def test_services(self):
        compose_list = [
            key
            for key in self.compose.services
            if isinstance(self.compose.services[key], dict)
        ]
        self.assertEqual(len(compose_list), 6)
        for name in compose_list:
            self.assertTrue(
                name
                in [
                    "django",
                    "django-worker",
                    "portainer",
                    "django-redis",
                    "postgres",
                    "flask",
                ]
            )

    def test_volumes(self):
        self.assertDictEqual(self.compose.volumes, {"postgres-app-data": None})

    def test_networks(self):
        self.assertDictEqual(self.compose.networks, {"backend": {"driver": "bridge"}})

    def test_compose_list_is_invalid(self):
        self.compose.list_path = []
        with self.assertRaises(ValueError):
            self.compose.is_valid

    def test_is_image(self):
        self.assertTrue(self.compose.is_image("django-worker"))
        self.assertFalse(self.compose.is_image("django"))

    def test_get_build_path(self):
        full_path = self.compose.get_build_path("django")
        self.assertEqual(full_path, os.path.join(self.compose.base_path, "django_app"))

    def test_get_from_service(self):
        environment_dict = self.compose.get_from_service("django", "environment")
        self.assertDictEqual(environment_dict, {"DEBUG": "True"})
