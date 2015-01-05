# -*- coding: utf-8 -*-
"""

"""
# Copyright (c) 2014, Jason Jacobs

# Third party imports

from ..qt_bindings import QtGui, QtCore, Qt

# Local Imports
#import pdb
import copy
import functools

class State:
    """ Deprecated.  Use ToolState instead.
    """
    def __init__(self, name=None, desc=None):
        self.name = name
        self.desc = desc

class ToolState:
    def __init__(self, name=None, desc=None, tool=None, view=None):
        self.name = name
        self.desc = desc
        self.tool = tool
        self.view = view

    def handle(self, event, method_name=''):
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            result = method(event)
            return result
        else:
            return False

class Tool(object):
    """ Provides mouse and key bindings to View objects.

    Possible bindings include:
        virtual void    contextMenuEvent ( QContextMenuEvent * event )
        virtual void    dragEnterEvent ( QDragEnterEvent * event )
        virtual void    dragLeaveEvent ( QDragLeaveEvent * event )
        virtual void    dragMoveEvent ( QDragMoveEvent * event )
        virtual void    dropEvent ( QDropEvent * event )
        virtual bool    event ( QEvent * event )
        virtual void    focusInEvent ( QFocusEvent * event )
        virtual bool    focusNextPrevChild ( bool next )
        virtual void    focusOutEvent ( QFocusEvent * event )
        virtual void    inputMethodEvent ( QInputMethodEvent * event )
        virtual void    keyPressEvent ( QKeyEvent * event )
        virtual void    keyReleaseEvent ( QKeyEvent * event )
        virtual void    mouseDoubleClickEvent ( QMouseEvent * event )
        virtual void    mouseMoveEvent ( QMouseEvent * event )
        virtual void    mousePressEvent ( QMouseEvent * event )
        virtual void    mouseReleaseEvent ( QMouseEvent * event )

    """
    # Style maps are class variables
    style_map = {}

    def __init__(self, parent, snap=False, name="Base Tool"):
        self.parent = parent
        self.snap = snap
        self.name = name
        self.view_mode = None

    def coords(self, event):
        point = self.parent.mapToScene(event.x(), event.y())
        x = point.x()
        y = point.y()
        if self.snap is True:
            x, y = self.parent.snap_coords(x, y)
        return QtCore.QPointF(x, y)

    def get_style(self):
        return None

    def __repr__(self):
        return "{}()".format(self.name.replace(" ", ""))

    def __call__(self, *args, **kwargs):
        print("copy tool")
        return copy.deepcopy(self)



def make_handler(method_name):
    def wrapper(self, event):
        return self.state.handle(event, method_name)
    return wrapper

def stateful_class(cls):
    for method_name in ['mouseReleaseEvent',
                        'mousePressEvent',
                        'mouseDoubleClickEvent',
                        'mouseMoveEvent',
                        'keyReleaseEvent',
                        'keyPressEvent',
                        ]:
        setattr(cls, method_name, make_handler(method_name))
    return cls
