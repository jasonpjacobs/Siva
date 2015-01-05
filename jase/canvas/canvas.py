# -*- coding: utf-8 -*-
"""

Copyright (c) 2014, Jason Jacobs
"""


# Python Imports
#import sys, os, pdb
from pdb import set_trace as db
import collections

# Third party imports
import numpy as np
from ..qt_bindings import QtGui, QtCore, Qt


# Local Imports
from .tools import Tool
from .pan_tool import PanTool
from .zoom_tool import ZoomTool
from .selection_tool import SelectionTool
from .move_tool import MoveTool
from .edit_tool import EditTool
from .styles import ColorHighlighter
from .connections import ConnectionTool

from .view import View

class Canvas(QtGui.QGraphicsScene):
    """
    A 2D Canvas on which to draw and interact with items.

    This class provides a streamlined interface to the QGraphic* classes.
    """
    def __init__(self, height=400, width=800, scale=1.0, *args, **kwargs):
        '''
        '''
        QtGui.QGraphicsScene.__init__(self)

        # Geometry
        self.size = (width, height)
        self.scale = scale

        # Continue initialization
        self._setup_scene()

        # Stylizers:  Used control how canvas items are rendered
        self.style_map = {}
        self._load_styles()

        # Keybindings
        self.load_key_bindings()

        # Tools
        self.tools = []
        self.default_tools()
        self.active_tools = []

        # The "main" view
        self._view = View(canvas=self)

    # ----------------------------------------------------------------
    #    Properties
    # ----------------------------------------------------------------
    @property
    def height(self):
        return self.size[1]

    @height.setter
    def height(self, value):
        self.size[1] = value

    @property
    def width(self):
        return self.size[0]

    @width.setter
    def width(self, value):
        self.size[0] = value

    # ----------------------------------------------------------------
    #    User level methods
    # ----------------------------------------------------------------
    def zoom(self, x=None, y=None):
        assert not((x is None) and (y is None))
        if x is None:
            x = y
        if y is None:
            y = x
        self._view.scale(x, y)

    def add(self, items):
        if isinstance(items, QtGui.QGraphicsItem):
            items=[items,]
        for item in items:
            if hasattr(item,'parent') and item.parent is None:
                item.parent = self
            self.addItem(item)

    # ----------------------------------------------------------------
    #    Properties
    # ----------------------------------------------------------------

    # ----------------------------------------------------------------
    #    Internal methods
    # ----------------------------------------------------------------
    def _setup_scene(self):
        """Initializes the QGraphicsScene.

        Called during Canvas initialization. Currently, just sets the size.
        """

        # The bounds argument keeps track of the Canvas area that is drawable
        self.bounds = QtCore.QRect(0, 0, self.size[0], self.size[1])

        # We set the scene rect to be larger than the desired bounds so we can
        # zoom and pan as desired near the edges of the canvas

        self.setSceneRect(QtCore.QRectF(
            self.bounds.adjusted(-self.size[0], -self.size[1],
            self.size[0], self.size[1]))
            )

    def _load_styles(self):
        self.ch = ColorHighlighter()
        self.style_map["highlight"] = self.ch

    def default_tools(self):
        """Method to define applicable view tools.

        Can by overridden by subclasses to add additional tools
        """
        for tool in (PanTool, ZoomTool, SelectionTool, MoveTool, ConnectionTool, EditTool):
            self.add_tool(tool)

    def add_tool(self, tool):
        assert(issubclass(tool, Tool))
        self.tools.append(tool)
        self.style_map.update(tool.style_map)

    def load_key_bindings(self):
        """Stores View specific key bindings in a dict.

        Hard coded for now.
        TODO:  Load from the QSettings class
        """
        kb = {
              "Pan Right": Qt.Key_Right,
              "Pan Left": Qt.Key_Left,
              "Pan Up": Qt.Key_Up,
              "Pan Down": Qt.Key_Down,
              "Mouse Pan Button": Qt.LeftButton,
              "Box Zoom Button": Qt.LeftButton,
              "Mouse Zoom Button": Qt.RightButton,
              "Box Zoom": Qt.Key_Z,
              "Zoom Fit": Qt.Key_F,
              "Zoom Box": Qt.Key_Z,
              "Cancel": Qt.Key_Escape
        }
        self.bindings = kb
