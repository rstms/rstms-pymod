#!/usr/bin/env python3

import sys
from pathlib import Path

import click
import click.core
from tomlkit import dumps, parse

from .exception_handler import ExceptionHandler
from .shell import _shell_completion
from .version import __timestamp__, __version__

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"


def _ehandler(ctx, option, debug):
    ctx.obj = dict(ehandler=ExceptionHandler(debug))
    ctx.obj["debug"] = debug


def _cat(project):
    click.echo(dumps(project))


@click.group("pymod", context_settings={"auto_envvar_prefix": "PYMOD"})
@click.version_option(message=header)
@click.option(
    "--shell-completion",
    is_flag=False,
    flag_value="[auto]",
    callback=_shell_completion,
    help="configure shell completion",
)
@click.option(
    "-d",
    "--debug",
    is_eager=True,
    is_flag=True,
    callback=_ehandler,
    help="debug mode",
)
@click.option(
    "-t",
    "--toml-file",
    type=click.Path(
        dir_okay=False, exists=True, writable=True, path_type=Path
    ),
    default="./pyproject.toml",
    help="pyproject.toml file",
)
@click.pass_context
def pymod(ctx, toml_file, debug, shell_completion):
    """tools for manipulating pyproject.toml"""
    ctx.obj.update(
        dict(toml_file=toml_file, project=parse(toml_file.read_text()))
    )


@pymod.command
@click.pass_context
def cat(ctx):
    """write project file to stdout"""
    project = ctx.obj["project"]
    _cat(project)


@pymod.command
@click.option("-d", "--dev", is_flag=True, help="add dev dependency")
@click.argument("module", type=str)
@click.pass_context
def add(ctx, dev, module):
    """add a module to the project's [dev] dependencies"""
    project = ctx.obj["project"]
    _cat(project)


if __name__ == "__main__":
    sys.exit(pymod())  # pragma: no cover
