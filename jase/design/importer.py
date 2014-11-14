import types
import sys
import os

from jase.design.library import Library
class DB:
    pass

from importlib._bootstrap import SourceFileLoader

class DesignLoader(SourceFileLoader):
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
            base_path = self.lib_defs[fullname]
            full_path = os.path.join(base_path, '__init__.py')
            #return Loader(fullname, full_path)
            return self
        return None

    def load_module(self, fullname):
        if fullname in sys.modules:
            module = sys.modules[fullname]
        else:
            path = self.lib_defs[fullname]
            module = Library(name=fullname, path=path)
            sys.modules[fullname] = module

        module.__loader__ = self
        module.__path__ = [self.lib_defs[fullname]]
        code = self.get_code(fullname)
        exec(code, module.__dict__)

    def get_filename(self, name):
        root = self.lib_defs[name]
        path = os.path.join(root, '__init__.py')
        return path


class Loader(SourceFileLoader):
    pass