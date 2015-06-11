# -*- coding: utf-8 -*-
# Copyright (c) 2014, Jason Jacobs

# Third party imports

from ..qt_bindings import QtGui, QtCore, Qt

# Local Imports
from .tools import Tool, State
#import pdb



class MoveTool(Tool):
    """The move tool will let the use move a selected set of items
    on the canvas via the mouse.

    There are two modes of operation.  In ad-hoc mode, 
    any movable item under the mouse can be moved via a
    mouse drag.

    There is also a precision mode, activated via the M key,
    that will move the selected set of item.  The first mouse
    click sets the origin, and the second click sets the move
    delta.

    """

    Idle = State("Idle")
    ReadyToDrag = State("ReadyToDrag")
    Precision = State("Precision")
    Dragging = State("Dragging")
    WaitForClick = State()

    def __init__(self, *args, **kwargs):
        super(MoveTool, self).__init__(*args, **kwargs)
        self.name = "Move Tool"
        self.state = self.Idle
        self.snap = True
        self.precise_move_key = Qt.Key_M
        self.escape_key = Qt.Key_Escape

        self.reset()

    def keyReleaseEvent(self, event):
        if event.key() == self.precise_move_key:
            self.state = self.Precision
            self.parent.activateTool(self)
            return True
        elif event.key() == self.escape_key:
            # Move the selected items back to their original 
            # location
            if self.items:
                self.moveItems(self.items, self.origin)
            return True  
        else:
            return False

    def mousePressEvent(self, event):
        #print("Movetool mouse press")
        # Start an ad-hoc move
        if self.state is self.Idle:
            item = self.parent.itemAt(event.pos())
            if item is not None:
                if item.group():
                    item = item.group()
                # Remember where the drag was started
                self.click=event.pos()
                self.start = self.coords(event)
                self.items = (item,)
                self.state = self.ReadyToDrag
                self.parent.setCursor(Qt.ClosedHandCursor)
            return False
        
        elif self.state is self.Precision:
            # Start a precision move.
            self.start = self.coords(event)
            
            # Remember where the mouse started
            # in case we need to cancel the move
            self.origin = self.coords(event)
            
            # Capture the selected set
            self.items = self.parent.selected_items
            
            self.state = self.WaitForClick
            
            print("Click mouse to move items")
            return True
        
        elif self.state is self.WaitForClick:
            # Finish precise move
            print("Moving items")
            #items = self.items
            #self.moveItems(items, event)
            self.reset()
            return True
            
    def mouseMoveEvent(self, event):
        if self.state is self.Idle:
            if self.parent.itemAt(event.pos()) is not None:
                self.parent.setCursor(Qt.OpenHandCursor)
            else:
                self.parent.setCursor(Qt.ArrowCursor)
                return False
                
        elif self.state is self.ReadyToDrag and (
                event.buttons() & Qt.LeftButton):
            self.state = self.Dragging
            
        if self.state is self.Dragging:
            dest  = self.coords(event)
            self.moveItems(self.items, dest)
            return True
        elif self.state is self.WaitForClick:
            dest  = self.coords(event)
            self.moveItems(self.items, dest)
        else:
            return False 
        
    def mouseReleaseEvent(self, event):
        if self.state is self.Dragging:
            # The drag has finished.  Clear the move selection
            self.reset()
        elif self.state is self.WaitForClick:
            # Capture the event, so the release does not clear item
            # selections
            return True
        return False
    
    def moveItems(self, items, dest):
            delta = dest - self.start
            
            # Implement the move
            for item in self.items:
                pos = item.pos()
                item.setPos(pos + delta)
                item.update()
                
            # Update the origin for the next move event
            self.start = dest        

    def reset(self):
        self.state = self.Idle
        self.start = None
        self.end = None
        self.items = []
        
if __name__ == "__main__":
    from canvas import test
    from items import *
    test()