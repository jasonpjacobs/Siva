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

    def _load_cells(self):
        """Loads cell definitions from the file system.
        """
        assert self.path is not None
        assert os.path.isdir(self.path)

        subdirs = os.listdir(self.path)
        for subdir in subdirs:
            full_path = os.path.join(self.path, subdir)
            if os.path.isdir(full_path):
                c = Library.Placeholder(path=full_path)
                self.__cells__[subdir] = c