"""
Copyright (c) 2014, Jason Jacobs

@License
"""

# System Imports
import os, sys, logging
from pdb import set_trace as db

# Third party imports
from PySide import QtCore, QtGui
from PySide.QtCore import Qt

# Local Imports
from ..schematic import Schematic
from ..core.logging import WidgetHandler
from ..ui.console import Console

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
        app = QtGui.qApp
        self.setWindowTitle("{} - v{}".format(app.applicationName(), app.applicationVersion()))

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

        """
        QSplitter *parent = new QSplitter();
        QWidget *widget = new QWidget();
        QHBoxLayout *parentLayout = new QHBoxLayout();
        widget->setLayout(parentLayout);
        parent->addWidget(widget);
        QTabWidget *tabWidget = new QTabWidget();
        parentLayout->addWidget(tabWidget);

        setCentralWidget(parent);
        """

        # The main widget will be a tabbed widget where various editors
        # will be kept.  For now, just include a Canvas

        self.tabWidgetLeft = QtGui.QTabWidget()
        self.tabWidgetRight = QtGui.QTabWidget()


        splitter = QtGui.QSplitter(Qt.Horizontal)
        splitter.addWidget(self.tabWidgetLeft)
        splitter.addWidget(self.tabWidgetRight)

        sch = Schematic(width=1200, height=800)
        self.tabWidgetLeft.insertTab(0, sch, "Design - Old")
        sch = Schematic(width=1200, height=800)
        self.tabWidgetRight.insertTab(0, sch, "Design - New")

        sch = Schematic(width=1200, height=800)
        self.tabWidgetRight.insertTab(0, sch, "Opamp")

        self.setCentralWidget(splitter)

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
        #         Console Window
        # ----------------------------------------------------
        self.consoleDockWidget = QtGui.QDockWidget("Console", self)
        self.consoleDockWidget.setObjectName("ConsoleWidget")
        self.console = Console()
        self.consoleDockWidget.setWidget(self.console)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.consoleDockWidget)


        # ----------------------------------------------------
        #         Log Widget
        # ----------------------------------------------------
        self.logDockWidget = QtGui.QDockWidget("Log", self)
        self.logDockWidget.setObjectName("ListDockWidget")
        self.logWidget = QtGui.QTextEdit()
        self.logDockWidget.setWidget(self.logWidget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.logDockWidget)
        self.setup_logging(self.logWidget)


        self.tabifyDockWidget(self.consoleDockWidget, self.logDockWidget)

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

        self.info("JASE is now ready.")
        self.status("Ready.")

    def status(self, txt):
        self.statusBar().showMessage(txt)


    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

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

    def setup_logging(self, widget):
        logger = logging.getLogger(QtGui.qApp.applicationName())
        logger.setLevel(logging.DEBUG)

        handler = WidgetHandler(widget)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        self.logger = logger