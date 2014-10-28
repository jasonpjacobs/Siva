"""
Copyright (c) 2014, Jason Jacobs

@License
"""

# System Imports
import os, sys
from pdb import set_trace as db
import glob

# Third party imports
from PySide import QtCore, QtGui
from PySide.QtCore import Qt

# Local Imports
from ..schematic import Schematic

class App(QtGui.QApplication):
    """
    """
    def __init__(self):
        super().__init__(sys.argv)
        self.setApplicationName('Jase')
        self.setApplicationVersion('0.1 - Beta')

        # self.setWindowIcon()
        self.icons = {}
        self.load_icons()

    def load_icons(self):
        icons = glob.glob("../icons/*.png")
        pixmap = QtGui.QPixmap(100,100)
        pixmap.fill(QtGui.QColor("blue"))
        self.icons[''] = QtGui.QIcon(pixmap)
        for path in icons:
            dir, file_name = os.path.split(path)
            name = file_name.split('.')[0]
            self.icons[name] = QtGui.QIcon(path)

# ----------------------------------------------
#
# ----------------------------------------------
class Main(QtGui.QMainWindow):
    """
    """

    def __init__(self, parent=None, icons=[]):
        """

        The main window will have

        * Menubar
        * Button Bar
        * Central Dock area
        * Horizontal Dock Area
        * Status Bar
        """
        super().__init__(parent=parent)


        self.icons = QtGui.qApp.icons

        # ----------------------------------------------------
        #         Menu Bar
        # ----------------------------------------------------
        self.menubar = self.menuBar()

        self.define_filemenu()

        # ----------------------------------------------------
        #         Button Bar

        # ----------------------------------------------------

        # ----------------------------------------------------
        #         Editor Area
        # ----------------------------------------------------
        # The main widget will be a tabbed widget where various editors
        # will be kept.  For now, just include a Canvas
        self.tabWidget = QtGui.QTabWidget()
        self.setCentralWidget(self.tabWidget)
        sch = Schematic(width=1200, height=800)
        self.tabWidget.insertTab(0, sch, "New Schematic")

        #self.tabWidget.insertTab(1, Schematic(), "New Schematic")
        self.editorWidget = QtGui.QTabWidget()

        self.setCentralWidget(self.tabWidget)

        # ----------------------------------------------------
        #         Device Selector Widget
        # ----------------------------------------------------
        part_selector_dock_widget = QtGui.QDockWidget("Device Selector", self)
        part_selector_dock_widget.setObjectName("devselDockWidget")
        part_selector_dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)
        self.part_selector_widget = QtGui.QTableWidget()

        part_selector_dock_widget.setWidget(self.part_selector_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, part_selector_dock_widget)

        # ----------------------------------------------------
        #         Properties Widget
        # ----------------------------------------------------
        propertiesDockWidget = QtGui.QDockWidget("Properties", self)
        propertiesDockWidget.setObjectName("propertiesDockWidget")
        propertiesDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, propertiesDockWidget)
        self.propertiesWidget = QtGui.QTableWidget()
        propertiesDockWidget.setWidget(self.propertiesWidget)

        # ----------------------------------------------------
        #         Log Widget (ToDo:  Create actual log widget)
        # ----------------------------------------------------
        self.logDockWidget = QtGui.QDockWidget("Log", self)
        self.logDockWidget.setObjectName("ListDockWidget")
        self.logWidget = QtGui.QListWidget()
        self.logDockWidget.setWidget(self.logWidget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.logDockWidget)

        # ----------------------------------------------------
        #         Console Window
        # ----------------------------------------------------
        self.consoleDockWidget = QtGui.QDockWidget("Console", self)
        self.consoleDockWidget.setObjectName("ConsoleWidget")
        self.console = QtGui.QListWidget()
        self.consoleDockWidget.setWidget(self.console)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.consoleDockWidget)
        self.tabifyDockWidget(self.logDockWidget, self.consoleDockWidget)

        # ----------------------------------------------------
        #         Hierarchy Widget
        # ----------------------------------------------------
        self.hierarchyDockWidget = QtGui.QDockWidget("Hierarchy", self)
        self.hierarchyDockWidget.setObjectName("hierarchyDockWidget")
        #logDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)
        #self.hierarchyWidget = HierarchyWidget()
        #self.hierarchyDockWidget.setWidget(self.hierarchyWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.hierarchyDockWidget)


        # ----------------------------------------------------
        #         Status Bar
        # ----------------------------------------------------
        self.statusBar()

    def status(self, txt):
        self.statusBar().showMessage(txt)


    def define_actions(self):

        # ----------------------------------------------------
        #        Exit Application
        # ----------------------------------------------------
        exitAction = QtGui.QAction(Icons["filequit"], '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

    def define_filemenu(self):
        menubar = self.menubar
        fileMenu = menubar.addMenu('&File')

        # ----------------------------------------------------
        #        New
        # ----------------------------------------------------
        newAction = QtGui.QAction(self.icons['folder_add'], '&New', self)
        newAction.setShortcut('Ctrl+N')
        newAction.setStatusTip('New design')
        newAction.triggered.connect(self.file_new)
        fileMenu.addAction(newAction)

        # ----------------------------------------------------
        #        Open
        # ----------------------------------------------------
        openAction = QtGui.QAction(self.icons['folder'], '&Open...', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open design')
        openAction.triggered.connect(self.file_open)
        fileMenu.addAction(openAction)

        # ----------------------------------------------------
        #        Save
        # ----------------------------------------------------
        saveAction = QtGui.QAction(self.icons[''], '&Save...', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save design')
        saveAction.triggered.connect(self.file_save)
        fileMenu.addAction(saveAction)

        # ----------------------------------------------------
        #        Save As
        # ----------------------------------------------------
        saveAsAction = QtGui.QAction(self.icons[''], '&Save As...', self)
        saveAsAction.setStatusTip('Save design as..')
        saveAsAction.triggered.connect(self.file_save_as)
        fileMenu.addAction(saveAsAction)


        # ----------------------------------------------------
        #        Exit
        # ----------------------------------------------------
        exitAction = QtGui.QAction(self.icons[''], '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)
        fileMenu.addAction(exitAction)

        self.fileMenu = fileMenu

    def file_new(self):
        raise NotImplementedError

    def file_open(self):
        raise NotImplementedError

    def file_save(self):
        raise NotImplementedError

    def file_save_as(self):
        raise NotImplementedError
