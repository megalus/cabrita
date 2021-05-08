"""Base utils module."""
import os
import re
import subprocess
from pathlib import Path

from buzio import formatStr


def run_command(task, get_stdout=False):
    """Run subprocess command.

    The function will attempt to run the task informed and
    return a boolean for the exit code or the captured std from console.

    :arg: task (string): the command to run
    :arg: get_stdout (bool, optional): capture stdout
    :arg: run_stdout (bool, optional): capture and run stdout

    :return: bool or string

    """
    try:
        if get_stdout is True:
            ret = subprocess.check_output(task, shell=True)
        else:
            ret = subprocess.call(task, shell=True, stderr=subprocess.STDOUT)

        if ret != 0 and not get_stdout:
            return False
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except Exception:
        return False

    if not get_stdout or ret == 0:
        return True
    if isinstance(ret, bytes):
        return ret.decode("utf-8")
    else:
        return ret


def get_path(path: str, base_path: str) -> str:
    """Return real path from string.

    Converts environment variables to path
    Converts relative path to full path
    """

    def _convert_env_to_path(env_in_path):
        s = re.search(r"\${(\w+)}", env_in_path)
        if not s:
            s = re.search(r"(\$\w+)", env_in_path)
        if s:
            env = s.group(1).replace("$", "")
            name = os.environ.get(env)
            if not name:
                raise ValueError("Can't find value for {}".format(env))
            path_list = [
                part if "$" not in part else name for part in env_in_path.split("/")
            ]
            path = os.path.join(*path_list)
        else:
            raise ValueError("Cant find path for {}".format(env_in_path))
        return path

    if "$" in base_path:
        base_path = _convert_env_to_path(base_path)
    if "$" in path:
        path = _convert_env_to_path(path)
    if path.startswith("."):
        list_path = os.path.join(base_path, path)
        path = os.path.abspath(list_path)
    return path


def format_color(text: str, style: str, theme: str = None) -> str:
    """Format string with color using formatStr method."""
    func = getattr(formatStr, style)
    return (
        func(text, use_prefix=False, theme=theme)
        if theme
        else func(text, use_prefix=False)
    )


def persist_on_disk(operation, service, folder):
    """Persist or remove in disk the service which needs action."""
    base_path = str(Path.home())
    config_path = os.path.join(base_path, ".cabrita")
    file_path = os.path.join(config_path, folder, service)
    if operation == "add":
        with open(file_path, "w+") as file:
            file.write(service)
    else:
        if os.path.exists(file_path):
            os.remove(file_path)
