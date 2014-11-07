from jcanvas.canvas_widget import CanvasWidget
from PySide import QtCore, QtGui
from PySide.QtCore import Qt

from .editor import Editor

class SchematicEditor(CanvasWidget, Editor):
    def __init__(self, *args, **kwargs):
        CanvasWidget.__init__(self, *args, **kwargs)
        Editor.__init__(self)

        self.canvas._view.zoomRect(QtCore.QRect(0,0, self.canvas.width, self.canvas.height))

        self.createActions()

        self.setContextMenuPolicy(Qt.ActionsContextMenu)


    def createActions(self):
        icons = QtGui.qApp.icons
        action = QtGui.QAction('Add instance...', self)
        action.setIcon(icons["plugin_add"])
        self.add_instance_action = action
        self.addAction(action)

    def install_menu(self, menubar):
        menu = menubar.addMenu('Schematic')
        menu.addAction(self.add_instance_action)

    @property
    def icon(self):
        return QtGui.qApp.icons['plugin']