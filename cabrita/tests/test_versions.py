from unittest import TestCase, mock

import requests_mock

PYPI_TEXT = """{
  "releases": {
    "1.6.3": [
      {
        "comment_text": "",
        "digests": {
          "md5": "1234",
          "sha256": "1234"
        },
        "downloads": -1,
        "filename": "cabrita-1.6.3-py3-null-any.whl",
        "has_sig": false,
        "md5_digest": "1234",
        "packagetype": "bdist_wheel",
        "python_version": "py3",
        "size": 14649,
        "upload_time": "2018-04-04T17:49:38",
        "url": "https://files.pythonhosted.org/packages/88/1b/1234/cabrita-1.6.3-py3-null-any.whl"
      },
      {
        "comment_text": "",
        "digests": {
          "md5": "1234",
          "sha256": "1234"
        },
        "downloads": -1,
        "filename": "cabrita-1.6.3.tar.gz",
        "has_sig": false,
        "md5_digest": "1234",
        "packagetype": "sdist",
        "python_version": "source",
        "size": 11062,
        "upload_time": "2018-04-04T17:49:39",
        "url": "https://files.pythonhosted.org/packages/6b/31/1234/cabrita-1.6.3.tar.gz"
      }
    ],
    "1.6.4": [
      {
        "comment_text": "",
        "digests": {
          "md5": "1234",
          "sha256": "1234"
        },
        "downloads": -1,
        "filename": "cabrita-1.6.4-py3-null-any.whl",
        "has_sig": false,
        "md5_digest": "1234",
        "packagetype": "bdist_wheel",
        "python_version": "py3",
        "size": 14710,
        "upload_time": "2018-04-11T21:15:30",
        "url": "https://files.pythonhosted.org/packages/92/a1/1234/cabrita-1.6.4-py3-null-any.whl"
      },
      {
        "comment_text": "",
        "digests": {
          "md5": "1234",
          "sha256": "1234"
        },
        "downloads": -1,
        "filename": "cabrita-1.6.4.tar.gz",
        "has_sig": false,
        "md5_digest": "1234",
        "packagetype": "sdist",
        "python_version": "source",
        "size": 11096,
        "upload_time": "2018-04-11T21:15:31",
        "url": "https://files.pythonhosted.org/packages/fc/a2/1234/cabrita-1.6.4.tar.gz"
      }
    ]
  }
}
"""


class TestVersions(TestCase):
    def test_versions(self):
        from cabrita.versions import versions

        with requests_mock.mock() as m:
            url = "https://pypi.python.org/pypi/cabrita/json"
            m.get(url, text=PYPI_TEXT)

            result = versions()
        self.assertListEqual(result, ["1.6.3", "1.6.4"])

    @mock.patch("buzio.console.confirm", return_value=False)
    @mock.patch("cabrita.versions.versions", return_value=["99.99.99"])
    def test_check_version(self, *mocks):
        from cabrita.versions import check_version

        result = check_version()
        self.assertEqual(result, "[31m99.99.99 (update available)[22m")

    @mock.patch("buzio.console.confirm", return_value=True)
    @mock.patch("buzio.console.run", return_value=True)
    @mock.patch("cabrita.versions.versions", return_value=["99.99.99"])
    def test_check_version_with_update(self, *mocks):
        from cabrita.versions import check_version

        with self.assertRaises(SystemExit) as cm:
            check_version()

        self.assertEqual(cm.exception.code, 0)
