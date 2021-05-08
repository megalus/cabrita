"""Version package.

Checks version number for upgrades in PyPI
"""
import sys
from typing import List, Optional

import requests
from buzio import console, formatStr
from pkg_resources import parse_version
from requests import RequestException

from cabrita import __version__


def versions() -> Optional[List[str]]:
    """Return the version list data from PyPI.

    :return: list
    """
    console.info("Checking for updates...")
    url = "https://pypi.python.org/pypi/cabrita/json"
    versions_list = None
    try:
        ret = requests.get(url, timeout=1)
        data = ret.json()
    except RequestException:
        return None
    if data:
        versions_list = list(data["releases"].keys())
        versions_list.sort(key=parse_version)
    return versions_list


def check_version() -> str:
    """Check if it is the latest version.

    Compares actual version vs last known
    version in PyPI, for upgrades

    :return:
        string
    """
    last_version = __version__
    version_data = versions()
    if version_data:
        last_version = version_data[-1]
    if parse_version(last_version) > parse_version(__version__) and (
        "rc" not in last_version
        and "b" not in last_version
        and "dev" not in last_version
    ):
        console.warning(
            "You're running a outdated version.\n"
            + "Last Version: {}\n".format(last_version)
        )
        ret = console.confirm("Do you want to upgrade?")
        if ret:
            result = console.run("sudo pip3 install -U cabrita")
            if result:
                console.success("\nOperation complete. Please run again.")
            else:
                console.error("\nThere is a error during upgrade. Please try again.")
            sys.exit(0)
        else:
            return formatStr.error(
                "{} (update available)".format(last_version), use_prefix=False
            )
    return formatStr.success(last_version, use_prefix=False)
