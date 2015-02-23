from ..qt_bindings import QtGui, QtCore
import logging
import sys, os
import collections

from .package import Package, PlaceHolder


class LibDefs(collections.OrderedDict):
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
        dirs.sort()
        for dir in dirs:
            if dir.startswith('_') or dir.startswith('.'):
                continue
            full_path = os.path.join(path, dir)
            if os.path.isdir(full_path):
                try:
                    self.logger.info("Reading library {}".format(dir))
                    self[dir] = full_path
                except ValueError as e:
                    self.logger.error("Could not read library {}: {}".format(dir, sys.exc_info()[0]))

class Library(Package):
    @property
    def __cells__(self):
        return self._items

    @__cells__.setter
    def __cells__(self, value):
        self._items = value

    def _load_items(self):
        """Loads cell definitions from the file system.
        """
        assert self.path is not None
        assert os.path.isdir(self.path)

        dirs = [name for name in os.listdir(self.path) if not name.startswith('_')]
        dirs.sort()

        for subdir in dirs:
            full_path = os.path.join(self.path, subdir)
            if os.path.isdir(full_path):
                self._items[subdir] = PlaceHolder(name=subdir, parent = self.name)
