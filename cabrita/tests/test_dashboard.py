import contextlib
from io import StringIO
from unittest import TestCase, mock
from unittest.mock import MagicMock, Mock

from dashing.dashing import Split

from cabrita.components.box import Box
from cabrita.components.config import Config
from cabrita.components.dashboard import Dashboard
from cabrita.tests import LATEST_CONFIG_PATH


class TestDashboard(TestCase):
    def setUp(self):
        self.dummyWatch = Box()
        self.config = Config()
        self.config.add_path(LATEST_CONFIG_PATH)
        self.config.load_file_data()
        self.assertTrue(self.config.is_valid)
        self.dashboard = Dashboard(self.config)
        self.dashboard.compose_watch = self.dummyWatch
        self.dashboard.user_watches = self.dummyWatch
        self.dashboard.system_watch = self.dummyWatch
        self._create_box()

    def _create_box(self):
        inspect_mock = Mock()
        inspect_mock.interval = 6
        self.box = Box(docker=inspect_mock, git=inspect_mock)
        self.box.data = {"interval": 15, "name": "Test Box"}
        self.box._services = ["Test App1", "TestApp2"]

    def test_all_boxes(self):
        self.assertListEqual(
            self.dashboard.all_boxes,
            [self.dummyWatch, self.dummyWatch, self.dummyWatch],
        )

    def test__log_box(self):
        temporary_stdout = StringIO()
        response = (
            "[36mInfo: Box 'Test Box' added. Inspecting docker containers each 6 seconds. "
            "Inspecting git repositories each 6 seconds. Refreshing data each 15.0 seconds. "
            "Services: Test App1, TestApp2.[22m"
        )
        with contextlib.redirect_stdout(temporary_stdout):
            self.dashboard._log_box(self.box)
        output = temporary_stdout.getvalue().strip()
        self.assertEqual(output, response)

    @mock.patch("cabrita.components.dashboard.Terminal")
    @mock.patch("cabrita.components.dashboard.Dashboard._get_layout")
    @mock.patch(
        "cabrita.components.dashboard.Dashboard._update_boxes",
        side_effect=KeyboardInterrupt(),
    )
    def test_run(self, *mocks):
        with self.assertRaises(SystemExit) as assert_exit:
            self.dashboard.run()

        self.assertEqual(assert_exit.exception.code, 0)

    def test_add_box(self):
        self.dashboard.add_box(self.box)
        self.assertTrue(len(self.dashboard.large_boxes), 1)

    @mock.patch("cabrita.components.dashboard.Pool", autospec=True)
    def test__update_boxes(self, *mocks):
        self.dashboard._update_boxes()
        self.assertIsInstance(self.dashboard.user_watches.widget, MagicMock)

    @mock.patch("blessed.Terminal")
    def test__get_layout(self, mock_terminal):
        self.assertIsInstance(self.dashboard._get_layout(mock_terminal), Split)
