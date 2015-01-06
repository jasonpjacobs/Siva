import types
import sys
import os
import importlib.abc
import imp
from jase.design.library import Library
from jase.design.cell import Cell
class DB:
    pass

from importlib._bootstrap import SourceFileLoader

class DesignFinder(importlib.abc.MetaPathFinder):
    def __init__(self, library_paths=None, name="DesignLoader"):
        if library_paths is None:
            library_paths = {}

        self.library_paths = library_paths
        self.name = name

    def install(self):
        """Installs this loader on the sys.meta_path"""
        sys.meta_path = [self] + sys.meta_path

    def find_module(self, fullname, path=None):
        """Looks to see if the requested module is a library or a cell that this loader will handle.

        If the name is in the library paths dictionary, it is loaded as a library.  If the given path
        is in the library list, the parent package is a library, and the module to be loaded is a cell
        """
        if fullname in self.library_paths:
            return LibLoader(name=fullname, path=self.library_paths[fullname], lib_defs=self.library_paths)
        elif path[0] in self.library_paths.values():
            name = fullname.rpartition('.')[-1]
            return CellLoader(name=name, path=os.path.join(path[0], name))
        return None


class Loader(SourceFileLoader):
    """
    """
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def get_filename(self, name):
        root = self.get_path(name)
        path = os.path.join(root, '__init__.py')
        return path

    def load_module(self, fullname):
        name = fullname.rpartition('.')[-1]
        ispkg = self.is_package(fullname)
        if fullname in sys.modules:
            module = sys.modules[fullname]
        else:
            path = self.path
            module = self.module_cls(name=name, path=path)

        module.__file__ = self.get_filename(fullname)
        if ispkg:
            module.__path__ = [self.path]
            module.__package__ = fullname
        else:
            module.__package__ = fullname.rpartition('.')[0]

        sys.modules[fullname] = module
        try:
            code = self.get_code(fullname)
            exec(code, module.__dict__)
        except FileNotFoundError:
            #raise ImportError("{} is not a package.".format(fullname))
            pass
        module._load_items()
        return module


class LibLoader(Loader):
    lib_paths = {}
    module_cls = Library
    def __init__(self, name, path, lib_defs):
        super().__init__(name, path)
        LibLoader.lib_paths.update(lib_defs)

    def get_path(self, fullname):
        return self.path


class CellLoader(Loader):
    module_cls = Cell
    def get_path(self, fullname):
        return self.path
