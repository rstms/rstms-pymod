# cli tests

from difflib import Differ

import pytest

from rstms_pymod import Project


class FileDiff:
    def __init__(self):
        self.result = None

    def _lines(self, path):
        text = path.read_text()
        return list(filter(None, map(lambda s: s.rstrip(), text.splitlines())))

    def compare(self, old, new):
        assert old.is_file()
        assert new.is_file()
        self.old = old
        self.new = new
        self.old_lines = self._lines(old)
        self.new_lines = self._lines(new)
        self.result = list(Differ().compare(self.old_lines, self.new_lines))

        self.deleted = list(filter(lambda l: l[0] == "-", self.result))
        self.added = list(filter(lambda l: l[0] == "+", self.result))
        self.changed = list(filter(lambda l: l[0] == "?", self.result))

        self.deltas = {}
        self.match = True
        for n, line in enumerate(self.result):
            if line[0] in ["-", "+", "?"]:
                self.deltas[n] = line
                self.match = False

        return self


@pytest.fixture
def diff():
    def _diff(old=None, new=None):
        return FileDiff().compare(old, new)

    return _diff


@pytest.fixture
def project_file(shared_datadir):
    return shared_datadir / "pyproject.toml"


@pytest.fixture
def project(project_file):
    return Project(project_file)
