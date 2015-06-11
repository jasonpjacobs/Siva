# -*- coding: utf-8 -*-
"""
Defines a Widget used to draw and edit basic shapes.
"""


import sys

from ..qt_bindings import QtGui, QtCore, Qt

from .canvas_widget import CanvasWidget
from .canvas import Canvas

from .icons  import icons_rc

import pdb

class DrawingWidget(QtGui.QWidget):

    def __init__(self):
        QtGui.QWidget.__init__(self)


        icon = QtGui.QIcon(":/disk.png")
        self.initUI()


    def initUI(self):
        layout = QtGui.QVBoxLayout()
        self.create_menu(layout)
        self.create_canvas(layout)
        self.setLayout(layout)


    def create_tool_button(self, action):
        button = QtGui.QToolButton()
        button.setDefaultAction(action)

    def create_menu(self, layout):

        menubar = QtGui.QMenuBar()
        toolbar = QtGui.QToolBar()
        toolbar.setMovable(True)
        toolbar.setAllowedAreas(Qt.AllToolBarAreas)

        self.create_file_menu(menubar, toolbar)
        layout.addWidget(menubar)
        layout.addWidget(toolbar)

    def create_action(self, name, shortcut=None, method=None, tool_tip=None, icon=None, toolbar=None, menu=None):
        action = QtGui.QAction(name, self)

        if shortcut:
            action.setShortcut(shortcut)

        if tool_tip:
            action.setStatusTip(tool_tip)

        if icon:
            icon = QtGui.QIcon(icon)
            action.setIcon(icon)

        if method:
            action.triggered.connect(method)

        if toolbar:
            toolbar.addAction(action)

        if menu:
            menu.addAction(action)
        return action

    def create_file_menu(self, menubar, toolbar=None):
        fileMenu = menubar.addMenu('&File')

        self.create_action(name='Open', shortcut='Ctrl+O', tool_tip="Open drawing",
                           icon=':images/folder-open.png', method=self.file_open,
                           menu=fileMenu, toolbar=toolbar)

        self.create_action(name='Save', shortcut='Ctrl+S', tool_tip="Save drawing",
                           icon=':images/disk.png', method=self.file_save,
                           menu=fileMenu, toolbar=toolbar)

        self.create_action(name='Save as...', tool_tip="Save drawing",
                           icon=':images/disk--pencil.png', method=self.file_save,
                           menu=fileMenu, toolbar=toolbar)

        self.create_action(name='Close', shortcut='Ctrl+X', tool_tip="Close drawing",
                           icon=':images/folder-horizontal.png', method=self.file_close,
                           menu=fileMenu, toolbar=toolbar)

    def create_canvas(self, layout):
        widget = CanvasWidget(canvas=Canvas())
        layout.addWidget(widget)

    def file_open(self):
        print("Open file")

    def file_close(self):
        pass

    def file_save(self):
        pass

    def file_save_as(self):
        pass

    # -----------------------------------------------------------------------------
    #               Actions
    # -----------------------------------------------------------------------------

    def move_front(self):
        pass

    def move_back(self):
        pass

    def move_forward(self):
        pass

    def move_backward(self):
        pass

    def rotate(self):
        pass

    def flip(self):
        pass




