"""
A set of classes for making and editing connections.
"""

from ..qt_bindings import QtCore, QtGui, Qt


from .tools import Tool, ToolState, stateful_class
from .items import Item, Group, Polyline

import pdb

class Connector(object):
    """ Mix-in class for any Item subclass that can accept connections.
    """
    _n = 0
    def __init__(self, direction=None, connection=None):
        self.connection = connection
        self.direction = direction

        self._n = self._n + 1
        #self.setCursor(Qt.CrossCursor)

    def get_connection_point(self, pos):
        return self.pos()

    def add_connection(self, connection):
        self.connection = connection
        return True

    def __repr__(self):
        return "Conn[{}]".format(self._n)
    def __str__(self):
        return self.__repr__()

class WireSegment(Polyline):
    pass

class Connection(Group):
    """ Base class for various types of connections between
    Canvas items
    """
    def __init__(self, points=None, *args, **kwargs):
        Group.__init__(self, *args, **kwargs)

        self.current_segment = None
        self.segments = []

        if points is not None:
            self.current_segment = WireSegment(color='blue', width=3, points=points)
            self.addToGroup(self.current_segment)
            self.segments.append(self.current_segment)

    def add_point(self, point):
        if self.current_segment is None:
            self.current_segment = WireSegment(color='blue', width=3)
            self.addToGroup(self.current_segment)
        self.current_segment.add_point(point)

    def add_connection(self, conn):
        print("Adding conn {} to {}".format(conn, self))
        for item in conn.segments:
            self.addToGroup(item)

    def cancel_segment(self):
        if self.current_segment:
            self.current_segment.points = self.current_segment.points[:-1]
            if len(self.current_segment.points) == 0:
                self.removeFromGroup(self.current_segment)




@stateful_class
class ConnectionTool(Tool):
    """

    Mouse move:  When the mouse is moved, the tool should look at any connectable items
    within a certain (configurable) distance to the cursor, in screen coordinates.

    Connectable items should advertise themselves in someway:  Outline color, bolding, highlighting.


    State:  No connections started:
    * Mouse click:
      -- on a connectable:  Start a wire, add connection reference to item
      -- on an item:  If the items accepts a connection, let it create a connection point, and accept the connection.
      -- on a blank space:  Start a wire?
      -- on a connection:  Start a new wire segment, use the existing connection.

    State:  Source connected
    Mouse click:
     == On blank canvas:  Complete a wire segment to the current location
     -- on a connectable:  Complete the wire segment,  Add connection reference to the connectable item.
    --


    Mouse click:
    [No connections]
    !) Click on empty space:  Start a wire
    2) Click on a connectable item:  Start a wire, and provide item with reference to the connection.


    States:
    1) Idle:
        'w' key --> Wiring mode
    1) WaitForClick:
        click:
            connectable? -->
                Create a new connection.
                Request coords from connectable.
                Add point to connection
            Nothing?  --> Add point to connection
        escape:
            Deactivate tool
    2) Connection started

    """
    class BaseState(ToolState):
        def mouseMoveEvent(self, event):
            item = self.view.itemAt(event.pos())
            if item is not None:
                if isinstance(item, Connector):
                    item.highlight = True
                    item.update()
                    item.setCursor(Qt.CrossCursor)
                    self.tool.current_connector = item
            else:
                if self.tool.current_connector is not None:
                    self.tool.current_connector.highlight = False

        def keyPressEvent(self, event):
            print(event.key())
            if event.key() == Qt.Key_Escape:
                self.tool.state = self.tool.idle
                self.tool.current_connector
                self.tool.parent.deactivateTool(self.tool)
                return True

    class Idle(BaseState):
        def keyReleaseEvent(self, event):
            if event.key() == Qt.Key_W:
                print("Wire tool:  Idle->Active", event.key())
                print("Wiring mode")
                self.tool.state = self.tool.wait_for_click
                self.tool.parent.setCursor(Qt.CrossCursor)
                self.tool.parent.activateTool(self.tool)
                return True
            return False

        def keyPressEvent(self, event):
            return False

    class WaitForClick(BaseState):
        def mousePressEvent(self, event):
            item = self.view.itemAt(event.pos())

            if item is not None:
                print("click on", item)
                if not isinstance(item, Connector):
                    return False
                else:
                    # If there is an item and it is connectable,
                    # add the point to the connection
                    coords = item.get_connection_point()
            else:
                # If there is no item, start a connection here
                coords = self.tool.coords(event.pos())

            self.tool.current_connection = Connection(color='blue', points=(coords, coords))
            # self.tool.current_connection  = self.tool.connection_class

            self.tool.parent.scene().add(self.tool.current_connection)
            #self.tool.current_connection.add_point(coords)
            self.tool.state = self.tool.wiring_in_progress
            return True


        def mouseMoveEvent(self, event):
            item = self.view.itemAt(event.pos())
            self.tool.parent.setCursor(Qt.CrossCursor)
            if item is not None:
                if isinstance(item, Connector):
                    item.highlight = True
                    item.update()
                    item.setCursor(Qt.CrossCursor)
                    self.tool.current_connector = item
            else:
                if self.tool.current_connector is not None:
                    self.tool.current_connector.highlight = False

    class WiringInProgress(BaseState):
        def mousePressEvent(self, event):
            conn = self.tool.current_connection
            item = self.view.itemAt(event.pos())

            if item is not None:
                if not isinstance(item, Connection):
                    return False
                elif item is conn.current_segment or item is conn:
                    coords = self.tool.coords(event)
                else:
                    print("Item is ", item)
                    item.add_connection(conn)
                    coords = item.get_connection_point()
                    print("Idle")
                    self.tool.state = self.tool.idle
            else:
                coords = self.tool.coords(event)
            conn.add_point(coords)

        def mouseMoveEvent(self, event):
            coords = self.tool.coords(event)

            # Hacking for now...
            conn = self.tool.current_connection
            points = conn.current_segment.points
            points[-1] = coords
            old_brect = conn.boundingRect()
            conn.current_segment.points = points
            conn.current_segment.update()
            conn.update(old_brect.united(conn.boundingRect()))

        def mouseDoubleClickEvent(self, event):
            self.tool.finish()

        def keyPressEvent(self, event):
            if event.key() == Qt.Key_Escape:
                # Cancel the currently drawn segment
                conn = self.tool.current_connection.cancel_segment()
                self.tool.finish()
                return True


        @property
        def state(self):
            return self._state

        @state.setter
        def state(self, value):
            print("New state is ", state)
            self._state = value


    def __init__(self, parent,):
        Tool.__init__(self, parent=parent, name="ConnectionTool")

        self.current_connector = None
        self.current_connection = None

        self.connection_class = Connection

        # Tool state instances
        self.idle = ConnectionTool.Idle(tool=self, view=parent)
        self.wait_for_click = ConnectionTool.WaitForClick(tool=self, view=parent)
        self.wiring_in_progress = ConnectionTool.WiringInProgress(tool=self, view=parent)

        self.state = self.idle
        self.snap = True
        #self.parent.activateTool(self)

    def finish(self):
        self.state = self.idle
        self.current_connection.current_segment = None
        self.current_connection = None




