"""Cabrita main module."""
import os
import shutil
import sys
from pathlib import Path

import click
import sentry_sdk
from buzio import console

from cabrita import __version__
from cabrita.command import CabritaCommand
from cabrita.components import BoxColor
from cabrita.versions import check_version

CONFIG_PATH = os.path.join(str(Path.home()), ".cabrita")


@click.command()
@click.option(
    "--path",
    envvar="CABRITA_PATH",
    default=None,
    help="Full path for configuration file.",
    type=click.Path(),
)
@click.option(
    "--color",
    default=None,
    help="Dashboard color (available options: {}).".format(
        ",".join(BoxColor.available_colors())
    ),
    type=click.Choice(BoxColor.available_colors()),
)
@click.argument("compose_path", type=click.Path(exists=True), nargs=-1)
def run(path, color, compose_path):
    """Run main command for cabrita.

    1. Check version
    2. Import configuration file
    3. Run dashboard.
    """
    try:
        print("")
        console.box("Cabrita v{}".format(__version__))
        version = check_version()
        if path:
            console.info("Loading Configuration...")
        command = CabritaCommand(
            cabrita_path=path,
            compose_path=compose_path,
            version=version,
            background_color=color,
        )
        if not command.has_a_valid_config:
            sys.exit(1)

        initialize_folder(["need_image", "need_update"])

        command.read_compose_files()
        if command.has_a_valid_compose:
            console.success("Configuration complete. Starting dashboard...")
            command.prepare_dashboard()
            command.execute()
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        raise


def initialize_folder(folder_list):
    """Initialize configuration folders."""
    for folder in folder_list:
        full_path = os.path.join(CONFIG_PATH, folder)
        shutil.rmtree(full_path, ignore_errors=True)
        os.makedirs(full_path, exist_ok=True)


if __name__ == "__main__":
    run()
