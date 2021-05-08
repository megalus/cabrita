"""Components Sub-Package.

This package has the cabrita components for:

| box = the Box class (the building block for the dashboard)
| config = the Config class (the data from cabrita.yml file)
| dashboard = the Dashboard class (convert boxes to dashing widgets and display it)
| docker = the DockerInspect class (the runner for inspect docker containers)
| git = the GitInspect class (the runner for inspect git data)
| watchers = the Watch class (the collection of internal and
| user watchers for the dashboard

"""
from enum import Enum
from typing import List


class BoxColor(Enum):
    """Enum using `Blessing`_ Colors values.

    .. _Blessing: https://pypi.python.org/pypi/blessings/

    Currently not working correctly.

    ======= ====== ======
    Color   Normal Bright
    ======= ====== ======
    black   0      8
    red     1      9
    green   2      10
    yellow  3      11
    blue    4      12
    magenta 5      13
    cyan    6      14
    white   7      15
    ======= ====== ======

    """

    black = 16
    grey = 0
    blue = 4
    cyan = 14
    yellow = 11
    white = 7

    @classmethod
    def available_colors(cls) -> List[str]:
        """Return available colors names.

        :return: List
        """
        return sorted(cls.__members__)
