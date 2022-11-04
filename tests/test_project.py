# tests for Project object

import pytest
from py_taplo import Taplo


@pytest.fixture
def test_project_init(project, shared_datadir):
    _file = shared_datadir / "pyproject.toml"
    assert _file.is_file()
    assert _file.read_text()
    assert project.doc
    assert project.path == _file
    assert project.path.parent == shared_datadir
    return project


def test_project_no_clobber(project):

    project_dir = project.path.parent
    pre_files = list(project_dir.iterdir())
    pre_data = project.path.read_text()
    with pytest.raises(PermissionError) as exc:
        project.write(backup=False)
    assert (
        exc.type is PermissionError
    ), "writing without backup or exists_ok should raise exception"
    post_files = list(project_dir.iterdir())
    assert pre_files == post_files
    post_data = project.path.read_text()
    assert pre_data == post_data


def test_project_write_backup(project):

    project_file = project.path
    project_dir = project.path.parent
    project_data = project.path.read_text()
    pre_files = list(project_dir.iterdir())
    project.write(exists_ok=True)
    post_files = list(project_dir.iterdir())
    assert project.path == project_file
    dst_data = project_file.read_text()
    assert project_data == dst_data
    new_files = set(post_files).difference(set(pre_files))
    assert len(new_files) == 1
    backup_file = new_files.pop()
    assert backup_file.is_file()
    print(f"{backup_file=}")
    assert backup_file.read_text() == project_data


def test_project_add_module(project, diff):
    old = project.write()
    assert str(old) != str(project.path)
    assert diff(old, project.path).match
    project.add_dependency("a-bridge")
    backup_file = project.write()
    assert not diff(backup_file, project.path).match
    assert diff(backup_file, old).match
    new = project.path

    taplo = Taplo()
    selector = "project.dependencies"
    old_deps = taplo.dict(old, selector)
    new_deps = taplo.dict(new, selector)

    assert old_deps != new_deps

    assert set(new_deps).difference(set(old_deps)) == set(["a-bridge"])


def test_project_delete_module(project, diff):
    project.delete_dependency("toml", "dev")
    old = project.write()
    new = project.path
    assert not diff(old, new).match
    taplo = Taplo()
    selector = "project.optional-dependencies.dev"
    old_deps = taplo.dict(old, selector)
    new_deps = taplo.dict(new, selector)
    assert len(old_deps) == 1 + len(new_deps)
    assert set(old_deps).difference(set(new_deps)) == set(["toml"])
