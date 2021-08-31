#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import typing
import urllib.request

logger = logging.getLogger("cli")

try:
    from clinner.command import Type, command
    from clinner.inputs import bool_input
    from clinner.run import Main
except Exception:
    logger.error("Package clinner is not installed, run 'pip install clinner' to install it")
    sys.exit(-1)

try:
    import toml
except Exception:
    toml = None

POETRY_URL = "https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py"


def poetry(*args) -> typing.List[str]:
    """
    Build a poetry command.

    :param args: Poetry command args.
    :return: Poetry command.
    """
    try:
        subprocess.run(
            shlex.split("poetry --version"), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )  # noqa
    except ImportError:
        if bool_input("Do you want to install Poetry?"):
            with tempfile.NamedTemporaryFile() as tmp_file, urllib.request.urlopen(POETRY_URL) as response:
                tmp_file.write(response.read())
                subprocess.run(shlex.split(f"python {tmp_file.name}"))
        else:
            logger.error("Poetry is not installed.")

    return shlex.split("poetry") + list(args)


@command(command_type=Type.SHELL, parser_opts={"help": "Install requirements"})
def install(*args, **kwargs):
    return [poetry("install", "-E", "full", *args)]


@command(command_type=Type.PYTHON, parser_opts={"help": "Clean directory"})
def clean(*args, **kwargs):
    for path in (".pytest_cache", "dist", "pip-wheel-metadata", "flama.egg-info", ".coverage", "test-results", "site"):
        shutil.rmtree(path, ignore_errors=True)


@command(
    command_type=Type.SHELL,
    args=((("-c", "--clean"), {"help": "Clean before build"}),),
    parser_opts={"help": "Build package"},
)
def build(*args, **kwargs):
    if kwargs["clean"]:
        clean()

    return [poetry("build", *args)]


@command(command_type=Type.SHELL, parser_opts={"help": "Black code formatting"})
def black(*args, **kwargs):
    return [poetry("run", "black", *args)]


@command(command_type=Type.SHELL, parser_opts={"help": "Flake8 code analysis"})
def flake8(*args, **kwargs):
    return [poetry("run", "flake8", *args)]


@command(command_type=Type.SHELL, parser_opts={"help": "Isort imports formatting"})
def isort(*args, **kwargs):
    return [poetry("run", "isort", *args)]


@command(command_type=Type.SHELL, parser_opts={"help": "Code lint using multiple tools"})
def lint(*args, **kwargs):
    return black() + flake8() + isort()


@command(command_type=Type.SHELL, parser_opts={"help": "Run tests"})
def test(*args, **kwargs):
    return [poetry("run", "pytest", *args)]


@command(command_type=Type.SHELL, parser_opts={"help": "Build docs"})
def docs(*args, **kwargs):
    return [poetry("run", "mkdocs", *args)]


@command(command_type=Type.SHELL, parser_opts={"help": "Upgrade version"})
def version(*args, **kwargs):
    return [poetry("version", *args)]


@command(
    command_type=Type.SHELL,
    args=((("-b", "--build"), {"help": "Build package", "action": "store_true"}),),
    parser_opts={"help": "Publish package"},
)
def publish(*args, **kwargs):
    cmds = []

    username = os.environ.get("PYPI_USERNAME")
    password = os.environ.get("PYPI_PASSWORD")

    if username and password:
        cmds.append(poetry("config", "http-basic.pypi", username, password))

    if kwargs["build"]:
        cmds += build(clean=True)

    cmds.append(poetry("publish"))

    return cmds


class Make(Main):
    commands = ("install", "clean", "build", "publish", "black", "flake8", "isort", "lint", "test", "version", "docs")


def main():
    return Make().run()


if __name__ == "__main__":
    sys.exit(main())
