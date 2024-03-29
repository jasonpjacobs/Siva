from ..canvas.canvas_widget import CanvasWidget
from ..qt_bindings import QtCore, QtGui, Qt
from ..icons import ICONS
from .editor import Editor

class SchematicEditor(CanvasWidget, Editor):
    def __init__(self, *args, **kwargs):
        CanvasWidget.__init__(self, *args, **kwargs)
        Editor.__init__(self)

        self.canvas._view.zoomRect(QtCore.QRect(0,0, self.canvas.width, self.canvas.height))

        self.createActions()

        self.setContextMenuPolicy(Qt.ActionsContextMenu)

        self.setAcceptDrops(True)

    def createActions(self):
        icons = ICONS
        action = QtGui.QAction('Add instance...', self)
        action.setIcon(icons["plugin_add"])
        self.add_instance_action = action
        self.addAction(action)

    def install_menu(self, menubar):
        menu = menubar.addMenu('Schematic')
        menu.addAction(self.add_instance_action)


    @property
    def icon(self):
        return ICONS['plugin']

    def dragEnterEvent(self, event):
        event.acceptProposedAction()