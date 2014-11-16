import os
import types

from PySide import QtGui

from jtypes import Typed, Str
from .view import View

class Cell(Typed):
    name = Str()
    def __init__(self, name=None, path=None, library=None):
        self.name = name
        self.path = path
        self.library = library

        if path is not None:
            self._load_views_from_path(path)

    def _load_views_from_path(self, path):
        for dir_name in os.listdir(path):
            # Look for available views
            if os.path.isdir(os.path.join(path, dir_name)):
                view = View(name=dir_name, path=os.path.join(path, dir_name))

            # Check for an icon
            if os.path.exists( os.path.join(self.path, 'icon.png')):
                self.icon = QtGui.QIcon(os.path.join(self.path, 'icon.png'))
            else:
                self.icon = None
