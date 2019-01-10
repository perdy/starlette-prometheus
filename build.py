#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import shlex
import sys

from clinner.command import Type, command
from clinner.run import Main


@command(command_type=Type.SHELL, parser_opts={"help": "Build package"})
def build(*args, **kwargs):
    return [shlex.split("npm install"), shlex.split("npm run build"), shlex.split("poetry build")]


@command(
    command_type=Type.SHELL,
    args=(
        (("--version",), {"help": "Version to upgrade", "choices": ("patch", "minor", "major")}),
        (("-b", "--build"), {"help": "Publish version", "action": "store_true"}),
    ),
    parser_opts={"help": "Build package"},
)
def publish(*args, **kwargs):
    cmds = []

    if kwargs.get("version", None):
        cmds.append(shlex.split(f"bumpversion {kwargs['version']}"))

    if kwargs["build"]:
        cmds += build()

    cmds.append(shlex.split("poetry publish"))

    return cmds


class Build(Main):
    commands = (
        "clinner.run.commands.black.black",
        "clinner.run.commands.flake8.flake8",
        "clinner.run.commands.isort.isort",
        "clinner.run.commands.pytest.pytest",
        "clinner.run.commands.tox.tox",
        "build",
        "publish",
    )


def main():
    return Build().run()


if __name__ == "__main__":
    sys.exit(main())
