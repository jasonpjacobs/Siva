"""
@License
"""

# System Imports
import os
import logging

# Third party imports
from PySide import QtGui
from PySide.QtCore import Qt

# Local Imports
from ..editors import SchematicEditor
from ..core.logging import WidgetHandler
from ..ui.console import Console
from ..ui.tab_widget import TabWidget
from ..ui.design_hierarchy_widget import DesignHierarchyWidget
from ..design.library import LibDefs
from ..ui.device_selector_widget import DeviceSelectorWidget


# ----------------------------------------------
#
# ----------------------------------------------
class Main(QtGui.QMainWindow):
    """
    """

    def __init__(self, parent=None):
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
        self.create_toolbars()

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

        self.tabWidgetLeft = TabWidget()
        self.tabWidgetRight = TabWidget()

        splitter = QtGui.QSplitter(Qt.Horizontal)
        splitter.addWidget(self.tabWidgetLeft)
        #splitter.addWidget(self.tabWidgetRight)

        self.setCentralWidget(splitter)

        # ----------------------------------------------------
        #         Device Selector Widget
        # ----------------------------------------------------
        part_selector_dock_widget = QtGui.QDockWidget("Device Selector", self)
        part_selector_dock_widget.setObjectName("devselDockWidget")
        part_selector_dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, part_selector_dock_widget)

        # ----------------------------------------------------
        #         Properties Widget
        # ----------------------------------------------------
        propertiesDockWidget = QtGui.QDockWidget("Properties", self)
        propertiesDockWidget.setObjectName("propertiesDockWidget")
        #propertiesDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)
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
        self.logger = None
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
        self.hierarchyDockWidget = QtGui.QDockWidget("Design Hierarchy", self)
        self.hierarchyDockWidget.setObjectName("hierarchyDockWidget")
        #logDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)
        #self.hierarchyWidget = HierarchyWidget()
        self.hierarchyWidget = DesignHierarchyWidget()
        self.hierarchyDockWidget.setWidget(self.hierarchyWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.hierarchyDockWidget)

        # ----------------------------------------------------
        #         Status Bar
        # ----------------------------------------------------
        self.statusBar()
        self.status("Ready.")

        self.read_libdefs()
        self.part_selector_widget = DeviceSelectorWidget(self.lib_defs)
        part_selector_dock_widget.setWidget(self.part_selector_widget)

    def read_libdefs(self):
        from ..design.importer import DesignLoader
        import db_root

        self.info("Reading library definitions")
        self.lib_defs = lib_defs = LibDefs(path=os.path.abspath(db_root.__path__[0]))
        loader = DesignLoader(lib_defs)
        loader.install()
        self.info("{} libraries read.".format(len(lib_defs)))

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
        exitAction = QtGui.QAction(self.icons["filequit"], '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

    def define_filemenu(self):
        menubar = self.menubar
        fileMenu = menubar.addMenu('&File')

        # ----------------------------------------------------
        #        New
        # ----------------------------------------------------
        newAction = QtGui.QAction(self.icons['folder_add'], '&New...', self)
        newAction.setShortcut('Ctrl+N')
        newAction.setStatusTip('New design')
        newAction.triggered.connect(self.file_new)
        fileMenu.addAction(newAction)
        self.newAction = newAction

        # ----------------------------------------------------
        #        Open
        # ----------------------------------------------------
        openAction = QtGui.QAction(self.icons['folder'], '&Open...', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open design')
        openAction.triggered.connect(self.file_open)
        fileMenu.addAction(openAction)
        self.openAction = openAction

        # ----------------------------------------------------
        #        Save
        # ----------------------------------------------------
        saveAction = QtGui.QAction(self.icons['disk'], '&Save...', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save')
        saveAction.triggered.connect(self.file_save)
        fileMenu.addAction(saveAction)
        self.saveAction = saveAction

        # ----------------------------------------------------
        #        Save As
        # ----------------------------------------------------
        saveAsAction = QtGui.QAction(self.icons['disk_multiple'], '&Save As...', self)
        saveAsAction.setStatusTip('Save as...')
        saveAsAction.triggered.connect(self.file_save_as)
        fileMenu.addAction(saveAsAction)
        self.saveAsAction = saveAsAction
        
        # ----------------------------------------------------
        #        Close
        # ----------------------------------------------------
        closeAction = QtGui.QAction(self.icons['folder_delete'], '&Close', self)
        closeAction.setStatusTip('Close')
        closeAction.triggered.connect(self.file_close)
        fileMenu.addAction(closeAction)
        self.closeAction = closeAction        

        # ----------------------------------------------------
        #        Exit
        # ----------------------------------------------------
        exitAction = QtGui.QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)
        fileMenu.addAction(exitAction)
        self.exitAction = exitAction

        self.fileMenu = fileMenu

    def file_new(self):
        self.new_view(editor=SchematicEditor)

    def file_open(self):
        raise NotImplementedError

    def file_save(self):
        raise NotImplementedError

    def file_save_as(self):
        raise NotImplementedError

    def file_close(self):
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

    def create_toolbars(self):
        self.file_toolbar = self.addToolBar("File")
        self.file_toolbar.addAction(self.newAction)
        self.file_toolbar.addAction(self.saveAction)
        self.file_toolbar.addAction(self.saveAsAction)
        self.file_toolbar.addAction(self.closeAction)

    def new_view(self, editor = None):
        """Loads a view into the central widget"""

        """
        sch = SchematicEditor(width=1200, height=800)
        self.tabWidgetLeft.insertTab(0, sch, "Design - Old")
        sch = SchematicEditor(width=1200, height=800)
        self.tabWidgetRight.insertTab(0, sch, "Design - New")

        sch = SchematicEditor(width=1200, height=800)
        self.tabWidgetRight.insertTab(0, sch, "Opamp")
        """
        inst = editor(width=1200, height=800)
        if hasattr(inst,'install_menu'):
            inst.install_menu(self.menubar)
        i = self.tabWidgetLeft.count()
        self.tabWidgetLeft.insertTab(0, inst, inst.icon, "New schematic: {}".format(i+1))

