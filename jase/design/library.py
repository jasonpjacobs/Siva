from PySide import QtGui
import logging
import sys, os
import types
import glob

import importlib
from .cell import Cell

class LibDefs(dict):
    """

    """
    def __init__(self, libs=None, path=None):
        if libs is None:
            libs = {}
        super().__init__(libs)
        self.logger = logging.getLogger(QtGui.qApp.applicationName())

        if path is not None and os.path.isdir(path):
            self._read_libs_in_path(path)
        else:
            self.logger.warn("Invalid path to LibraryDefinitions: {}".format(path))



    def _read_libs_in_path(self, path):
        self.logger.info("Reading libraries from {}".format(path))
        dirs = os.listdir(path)
        for dir in dirs:
            if dir.startswith('_') or dir.startswith('.'):
                continue
            full_path = os.path.join(path, dir)
            if os.path.isdir(full_path):
                try:
                    self.logger.info("Reading library {}".format(dir))
                    lib = Library(path=full_path, name=dir)
                    self[lib.name] = lib
                except ValueError as e:
                    self.logger.error("Could not read library {}: {}".format(dir, sys.exc_info()[0]))

class LazyLoad(dict):
    pass


class Library(types.ModuleType):
    """

    """

    class Placeholder:
        def __init__(self, path):
            self.path = path

    def __init__(self, name, full_name=None, path=None, desc=None, version=None, tags=None):
        """

        :param name: The name of the library.  Must not contain spaces.
        :param full_name:  The "full", or printer friendly library name.  May contain spaces.
        :param path: The path on the filesystem where the library resides
        :param desc: A text description of the library
        :param version:  The library version
        :param tags:
        :return:
        """
        super().__init__(name)

        self.name = name
        self.full_name = full_name
        self.desc = desc
        self.path = path
        self.version = version

        if tags is None:
            self.tags = {}
        else:
            self.tags = tags

        self.__cells__ = {}

        if os.path.isdir(path):
            self._load_cells()


    def __getattr__(self, attr):
        if attr in self.__cells__:
            return self.__cells__[attr]
        else:
            raise AttributeError


    # ------------------------------------------------------------------
    #   Dictionary interface
    # ------------------------------------------------------------------
    def __len__(self):
        return self.__cells__.__len__()

    def __getitem__(self, key   ):
        return self.__cells__.__getitem__(key)

    def __setitem__(self, key, value):
        # I can't think of a reason where a library (or cell) would need to
        # be modified.
        raise NotImplementedError("The cell dictionaries of a library are read only.")

        # But in case this changes in the future, we'll do this:
        #return self.__cells__.__setitem__(key, value)

    def __delitem__(self, key):
        return self.__cells__.__delitem__(self, key)

    def __iter__(self):
        return self.__cells__.__iter__()

    def keys(self):
        return self.__cells__.keys()

    def values(self):
        return self.__cells__.values()

    def items(self):
        return self.__cells__.items()


    def _load_cells(self):
        """Loads cell definitions from the file system.
        """
        assert self.path is not None
        assert os.path.isdir(self.path)

        subdirs = os.listdir(self.path)
        for subdir in subdirs:
            full_path = os.path.join(self.path, subdir)
            if os.path.isdir(full_path):
                c = Cell(name=subdir, path=full_path)
                self.__cells__[subdir] = c

