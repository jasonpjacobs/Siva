import os
import types
import collections

from PySide import QtGui, QtCore
from PySide.QtCore import Qt
from jtypes import Typed, Str


from .view import View
from .package import Package, PlaceHolder

class CellName(Str):
    def getIcon(self, obj):
        return obj.icon

class Cell(Package):
    def _load_items(self):
        dirs = [name for name in os.listdir(self.path) if not name.startswith('_')]
        dirs.sort()
        for dir_name in dirs:
            if os.path.exists( os.path.join(self.path, 'icon.png')):
                self.icon = QtGui.QIcon(os.path.join(self.path, 'icon.png'))
            else:
                if hasattr(QtGui.qApp, 'icons'):
                    self.icon = QtGui.qApp.icons['plugin']
                else:
                    self.icon = None

    @property
    def __views__(self):
        return self._items

    @__views__.setter
    def __view__(self, value):
        self._items = value

