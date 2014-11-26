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
    def __init__(self, lib_defs=None, name="DesignLoader"):
        if lib_defs is None:
            lib_defs = {}

        self.lib_defs = lib_defs
        self.name = name

    def install(self):
        """Installs this loader on the sys.meta_path"""
        sys.meta_path = [self] + sys.meta_path

    def find_module(self, fullname, path=None):
        print("Looking for module: {} in ({})".format(fullname, path))
        if fullname in self.lib_defs:
            return LibLoader(name=fullname, path=self.lib_defs[fullname], lib_defs=self.lib_defs)
        if "." in fullname:
            name = fullname.rpartition('.')[-1]
            print("Found cell",name)
            return CellLoader(name=name, path=os.path.join(path, name))
        return None


class Loader(SourceFileLoader):
    """
    The loader should set several attributes on the module. (Note that some of these attributes can change
    when a module is reloaded.)

    __name__
    The name of the module.

    __file__
    The path to where the module data is stored (not set for built-in modules).

    __cached__
    The path to where a compiled version of the module is/should be stored (not set when the attribute would be
    inappropriate).

    __path__
    A list of strings specifying the search path within a package. This attribute is not set on modules.

    __package__
    The parent package for the module/package. If the module is top-level then it has a value of the empty string. The
    importlib.util.set_package() decorator can handle the details for __package__.

    __loader__
    The loader used to load the module. (This is not set by the built-in import machinery, but it should be set whenever a loader is used.)
    """
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def get_filename(self, name):
        root = self.get_path(name)
        path = os.path.join(root, '__init__.py')
        print("    get_filename({}): {} ".format(name, path))
        return path

    def load_module(self, fullname):
        print("Loading module ", fullname)
        ispkg = self.is_package(fullname)
        if fullname in sys.modules:
            module = sys.modules[fullname]
        else:
            path = self.lib_defs[fullname]
            module = Library(name=fullname, path=path)

        mod.__file__ = "<%s>" % self.__class__.__name__
        module.__loader__ = self
        if ispkg:
            mod.__path__ = []
            mod.__package__ = fullname
        else:
            mod.__package__ = fullname.rpartition('.')[0]
        code = self.get_code(fullname)
        exec(code, module.__dict__)
        sys.modules[fullname] = module
        return module

class LibLoader(Loader):
    lib_paths = {}
    def __init__(self, name, path, lib_defs):
        super().__init__(name, path)
        LibLoader.lib_paths.update(lib_defs)

    def load_module(self, fullname):
        print("Loading module ", fullname)
        ispkg = self.is_package(fullname)
        if fullname in sys.modules:
            module = sys.modules[fullname]
        else:
            path = self.lib_paths[fullname]
            module = Library(name=fullname, path=path)

        module.__file__ = "<Library>"
        if ispkg:
            print(" {} is a package".format(fullname))
            module.__path__ = [self.path]
            module.__package__ = fullname
        else:
            print(" {} is a module".format(fullname))
            module.__package__ = fullname.rpartition('.')[0]
        code = self.get_code(fullname)
        exec(code, module.__dict__)
        sys.modules[fullname] = module
        return module

    def get_path(self, fullname):
        print("Getting path for ", fullname)
        if "." in fullname:
            libname, cellname = fullname.split('.')
            if libname in sys.modules:
                lib = sys.modules[libname]
            else:
                lib = __import__(libname)
            parent_dir = lib.__path__
            print("    lib is", parent_dir)

            path = os.path.join(parent_dir, cellname)
            print("    path is", path)
        else:
            path = self.lib_paths[fullname]
        return path


class CellLoader(Loader):
    def get_path(self, fullname):
        print("Getting path for cell ", fullname)
        if "." in fullname:
            libname, cellname = fullname.split('.')
            if libname in sys.modules:
                lib = sys.modules[libname]
            else:
                lib = __import__(libname)
            parent_dir = lib.__path__[0]
            print("    lib is", parent_dir)
            path = os.path.join(parent_dir, cellname)
            print("    path is", path)
            return path


    def load_module(self, fullname):
        if "." in fullname:
            libname, cellname = fullname.split('.')
            if libname in sys.modules:
                lib = sys.modules[libname]
            else:
                lib = __import__(libname)
            parent_dir = lib.__path__[0]
            #path = os.path.join(parent_dir, cellname)
            module = sys.modules.setdefault(fullname, imp.new_module(fullname))
            module.__file__ = self.path

            if self.is_package(fullname):
                module.__path__ = [os.path.split(module.__file__)[0]]
            else:
                module.__package__ = module.__package__.rpartition('.')[0]
            # module = Cell(name=fullname, path=self.path)
            module = sys.modules.setdefault(fullname, imp.new_module(fullname))
        else:
            raise NotImplementedError

        module.__loader__ = self
        module.__path__ = [path]
        code = self.get_code(fullname)
        exec(code, module.__dict__)
        sys.modules[fullname] = module

        print("Cell {} installed".format(fullname))
