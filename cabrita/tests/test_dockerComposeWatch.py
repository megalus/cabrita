from unittest import TestCase
from unittest.mock import MagicMock

from cabrita.components.config import Config
from cabrita.components.watchers import DockerComposeWatch
from cabrita.tests import LATEST_CONFIG_PATH


class TestDockerComposeWatch(TestCase):

    def setUp(self):
        inspector = MagicMock()
        self.config = Config()
        self.config.add_path(LATEST_CONFIG_PATH)
        self.config.load_data()
        self.watch = DockerComposeWatch(config=self.config, version=self.config.version, git=inspector,
                                        docker=inspector)

    def test__execute(self):
        response = \
            "-----------------------  ---------------  -\n" \
            "docker-compose           [33mBRANCH MODIFIED[22m  [36m [22m[37m[2m[22m\n" \
            "docker-compose.override  [33mBRANCH MODIFIED[22m  [36m [22m[37m[2m[22m\n" \
            "-----------------------  ---------------  -"
        self.watch._execute()
        self.assertEqual(self.watch._widget.text, response)
