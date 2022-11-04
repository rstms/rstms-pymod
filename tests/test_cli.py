# cli tests

import os
import shlex

import pytest
from click.testing import CliRunner
from py_taplo import Taplo

import rstms_pymod
from rstms_pymod import __version__, cli


def test_version():
    """Test reading version and module name"""
    assert rstms_pymod.__name__ == "rstms_pymod"
    assert __version__
    assert isinstance(__version__, str)


@pytest.fixture
def run():
    runner = CliRunner()

    env = os.environ.copy()
    env["TESTING"] = "1"

    def _run(cmd, **kwargs):
        assert_exit = kwargs.pop("assert_exit", 0)
        assert_exception = kwargs.pop("assert_exception", None)
        env.update(kwargs.pop("env", {}))
        kwargs["env"] = env

        result = runner.invoke(cli, cmd, **kwargs)

        while result.exception:
            if assert_exception:
                if isinstance(result.exception, assert_exception):
                    break
            raise result.exception from result.exception

        if assert_exit is not None:
            assert result.exit_code == assert_exit, (
                f"Unexpected {result.exit_code=} (expected {assert_exit})\n"
                f"cmd: '{shlex.join(cmd)}'\n"
                f"output: {str(result.output)}"
            )
        return result

    return _run


def test_cli_no_args(run):
    result = run([])
    assert "Usage:" in result.output


def test_cli_help(run):
    result = run(["--help"])
    assert "Show this message and exit." in result.output


def test_cli_exception(run):

    cmd = ["--shell-completion", "and_now_for_something_completely_different"]

    # example of testing for expected exception
    result = run(cmd, assert_exception=RuntimeError, assert_exit=None)
    assert result.exception
    assert result.exc_info[0] == RuntimeError
    assert result.exception.args[0] == "cannot determine shell"

    # example of a raised exception other than the expected one
    # this will break where the exception is raised
    # expecting TypeError but code raises RuntimeError
    with pytest.raises(RuntimeError) as exc:
        result = run(cmd, assert_exception=TypeError, assert_exit=None)
    assert exc
    assert exc.type is RuntimeError

    # example of catching the exception locally with pytest.raises
    with pytest.raises(RuntimeError) as exc:
        result = run(cmd)
    assert exc


def test_cli_exit(run):
    result = run(["--help"], assert_exit=None)
    assert result
    result = run(["--help"], assert_exit=0)
    assert result
    with pytest.raises(AssertionError):
        run(["--help"], assert_exit=-1)


def test_cli_add_module(run, project_file, shared_datadir, diff):
    old = shared_datadir / "old"
    old.write_text(project_file.read_text())

    cmd = ["--project-file", str(project_file), "add", "kniggits"]
    result = run(cmd)
    assert not result.output

    new = project_file

    d = diff(old, new)

    assert not d.match

    taplo = Taplo()
    selector = "project.dependencies"

    old_deps = taplo.dict(old, selector)
    new_deps = taplo.dict(new, selector)

    assert old_deps != new_deps

    assert set(new_deps).difference(set(old_deps)) == set(["kniggits"])
