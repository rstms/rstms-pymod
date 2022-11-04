#!/usr/bin/env python3

import sys
from pathlib import Path

import click
import click.core

from .exception_handler import ExceptionHandler
from .project import Project
from .shell import _shell_completion
from .version import __timestamp__, __version__

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"


def _ehandler(ctx, option, debug):
    ctx.obj = dict(ehandler=ExceptionHandler(debug))
    ctx.obj["debug"] = debug


def _cat(project):
    click.echo(str(project))


@click.group(name="pymod", context_settings={"auto_envvar_prefix": "PYMOD"})
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
    "-p",
    "--project-file",
    type=click.Path(
        dir_okay=False, exists=True, writable=True, path_type=Path
    ),
    default="./pyproject.toml",
    help="pyproject.toml file",
)
@click.pass_context
def cli(ctx, project_file, debug, shell_completion):
    """tools for manipulating pyproject.toml"""
    ctx.obj["project"] = Project(project_file)


@cli.command
@click.pass_context
def cat(ctx):
    """write project file to stdout"""
    project = ctx.obj["project"]
    _cat(project)


@cli.command
@click.option("-d", "--dev", "extra", flag_value="dev", help="dev/test")
@click.option("-D", "--doc", "extra", flag_value="docs", help="documentation")
@click.argument("module", type=str)
@click.pass_context
def add(ctx, module, extra):
    """add a module to the project [dev,doc] dependencies"""
    project = ctx.obj["project"]
    project.add_dependency(module, extra)
    project.write()
    return 0


@cli.command
@click.option("-d", "--dev", "extra", flag_value="dev", help="dev/test")
@click.option("-D", "--doc", "extra", flag_value="docs", help="documentation")
@click.argument("module", type=str)
@click.pass_context
def rm(ctx, module, extra):
    """remove a module from the project's [dev,doc] dependencies"""
    project = ctx.obj["project"]
    project.delete_dependency(module, extra)
    project.write()
    return 0


@cli.command
@click.option("-d", "--dev", "extra", flag_value="dev", help="dev/test")
@click.option("-D", "--doc", "extra", flag_value="docs", help="documentation")
@click.pass_context
def ls(ctx, extra):
    """list dependencies"""
    project = ctx.obj["project"]
    deps = project.dependencies(extra)
    for dep in deps:
        click.echo(dep)
    return 0


@cli.command
@click.pass_context
def fmt(ctx):
    """reformat pyproject.toml"""
    project = ctx.obj["project"]
    click.echo(project.fmt())
    return 0


@cli.command
@click.pass_context
def lint(ctx):
    """reformat pyproject.toml"""
    project = ctx.obj["project"]
    click.echo(project.lint())
    return 0


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
