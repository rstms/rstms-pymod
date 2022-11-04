# Project object represents pyproject.toml

import re
from pathlib import Path

from py_taplo import Taplo
from tomlkit import dumps, parse

from .utils import write_backup_file


class Project:
    def __init__(self, path=Path("pyproject.toml")):
        self.path = path
        self.read(path)

    def read(self, path):
        self.doc = parse(path.read_text())
        return self

    def write(self, path=None, backup=True, exists_ok=False):
        """write current document, returning filename written"""
        path = path or self.path
        ret = path
        if backup:
            ret = write_backup_file(self.path)
            exists_ok = True
        if exists_ok is False and path.exists():
            raise PermissionError
        self.path.write_text(dumps(self.doc))
        return ret

    def __str__(self):
        return dumps(self.doc)

    def _module_key(self, line):
        key = line
        if not line.startswith("@"):
            for sep in ["<=", "<", "!=", "==", ">=", ">", "~=", "==="]:
                if sep in line:
                    key, _, _ = line.partition(sep)
                    break
        m = re.match(r"[^[]*(\[[^]]*\]).*", line)
        if m:
            key += m.groups()[0]
        return key

    def _dependency_table(self, optional=None):
        if optional:
            selectors = ["project", "optional-dependencies", optional]
        else:
            selectors = ["project", "dependencies"]
        table = self.doc
        for selector in selectors:
            table = table[selector]
        return table

    def dependencies(self, optional=None):
        table = self._dependency_table(optional)
        module_list = list(table)
        return module_list

    def set_dependencies(self, module_list, optional=None):
        table = self._dependency_table(optional)
        for module in module_list:
            if module not in table:
                table.append(module)
        for module in table:
            if module not in module_list:
                table.remove(module)

    def add_dependency(self, module, optional=None):
        module_list = self.dependencies(optional)
        modules = {self._module_key(m): m for m in module_list}
        key = self._module_key(module)
        modules[key] = module
        module_list = list(modules.values())
        self.set_dependencies(module_list, optional)

    def delete_dependency(self, module, optional=None):
        module_list = self.dependencies(optional)
        modules = {self._module_key(m): m for m in module_list}
        key = self._module_key(module)
        modules.pop(key, None)
        module_list = list(modules.values())
        self.set_dependencies(module_list, optional)

    def fmt(self):
        """reformat pyproject.toml"""
        self.write()
        ret = Taplo().fmt(self.path, in_place=True)
        self.read
        return ret

    def lint(self):
        """verify syntax of pyproject.toml"""
        self.write()
        ret = Taplo().lint(self.path)
        self.read
        return ret
