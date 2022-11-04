# utility functions

from io import FileIO
from pathlib import Path
from tempfile import mkstemp


def write_backup_file(path, hidden=True, backup_dir=None):
    """write a backup copy of a file"""

    _dir = backup_dir or path.resolve().parent
    _prefix = ("." if hidden else "") + path.name + "."

    with path.open("rb") as ifp:
        fd, name = mkstemp(prefix=_prefix, dir=_dir, text=True)
        with FileIO(fd, "w") as ofp:
            ofp.write(ifp.read())

    return Path(name)
