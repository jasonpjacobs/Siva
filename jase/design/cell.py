import os
import types
import collections

from ..qt_bindings import QtGui, QtCore

from .package import Package
from ..design.view import View

class Cell(Package):
    def __init__(self, name, full_name=None, path=None, desc=None, version=None, tags=None):
        super().__init__(name, full_name=None, path=None, desc=None, version=None, tags=None)

        if path is not None and os.path.exists(path):
            if os.path.exists(os.path.join(path, 'icon.png')):
                self.icon = QtGui.QIcon(os.path.join(path, 'icon.png'))
        else:
            self.icon = QtGui.QApplication.instance().icons['processor']


    def _load_items(self):
        for k,v in self.__dict__.items():
            try:
                if issubclass(v, View):
                    self._items[k] = v
            except TypeError:
                pass

    @property
    def __views__(self):
        return self._items

    @__views__.setter
    def __view__(self, value):
        self._items = value

