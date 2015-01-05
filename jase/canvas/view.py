"""

"""

import collections
import numpy as np
from ..qt_bindings import QtGui, QtCore, Qt


class View(QtGui.QGraphicsView):
    """Extension of the QGraphicsView class to add pan/zoom tools, item
    selection, etc.
    """
    def __init__(self, canvas=None, grid_interval=100, tick_interval=20,
        dot_interval=10, origin=None):
        assert canvas is not None
        #assert canvas._scene is not None
        super(View, self).__init__(canvas)
        self.canvas = canvas

        # Scrolling
        policy = Qt.ScrollBarAlwaysOff
        self.setVerticalScrollBarPolicy(policy)
        self.setHorizontalScrollBarPolicy(policy)

        # Place holder drag behavior.
        # TODO:  Use tools to determine drag behavior
        #self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)

        # Enable caching of the view's background
        #self.setCacheMode(
        #    QtGui.QGraphicsView.CacheMode(QtGui.QGraphicsView.CacheBackground)
        #)

        # The BoundingRect mode seems to draw the background gradient completely.
        #self.setViewportUpdateMode(QtGui.QGraphicsView.SmartViewportUpdate)
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        #self.setViewportUpdateMode(
        #    QtGui.QGraphicsView.BoundingRectViewportUpdate)

        # If this is 'AnchorUnderMouse', the command line pan() method
        # is affected.  Instead, I just use no anchor here, and the
        # Zoom Tool re-centers the view around the mouse position
        # during a wheel zoom.

        #self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setTransformationAnchor(QtGui.QGraphicsView.NoAnchor)

        # This doesn't seem to matter
        self.setAlignment(Qt.AlignCenter)

        # Ensure the View receives mouse move events
        # even if a button is not pressed
        self.setMouseTracking(True)

        # View tools:  Pan, Zoom, Draw, Select, etc.
        self.tools = []
        self.active_tools = []
        for tool in canvas.tools:
            self.tools.append(tool(self))

        #TODO:  Set via QSettings
        self.grid = True
        self.grid_interval = grid_interval
        self.tick_interval = tick_interval
        self.dot_interval = dot_interval
        self.snap = 10

        # Set the origin, not currently used.
        self.origin = collections.namedtuple('origin', ['x', 'y'])
        if origin is None:
            origin = (0, 0)
        self.origin.x, self.origin.y = origin

        # Mouse coordinate tracking, for tools
        self.mouse_x = 0
        self.mouse_y = 0

        # Native QGraphicsScene coordinates increase
        # from the top to the bottom of the scene.
        # So we will scale the Y-axis
        self.scale(1, -1)

        # Selection box for tools
        self.selection_box = None

        self.selected_items = []




    # -------------------------------------------------------
    #    Event handling code
    # -------------------------------------------------------
    def restoreCursor(self):
        self.setCursor(Qt.ArrowCursor)

    def activateTool(self, tool):
        self.active_tools.insert(0, tool)
        self.canvas.active_tools = self.active_tools

    def deactivateTool(self, tool):
        if tool in self.active_tools:
            self.active_tools.remove(tool)
            self.canvas.active_tools = self.active_tools
        else:
            print("Error:  Tool {} not active, but requested deactivation.".format(tool))  # lint:ok

    def handle_event(self, event, event_type):
        """
        Handles mouse and keyboard events.

        When an event is given to the view to handle,
        this method goes through each tool in the stack
        and gives it an opportunity to handle the event.

        If none of the tools handle the event, continue
        event propagation
        """
        result = False

        # Give the active tool the first chance to handle an event
        for tool in self.active_tools:
            result = self.dispatch_event(tool, event_type, event)
            if result:
                return True

        # Then give the others tools a chance
        for tool in self.tools:
            result = self.dispatch_event(tool, event_type, event)
            if result:
                return True

        # None of the tools handled the event.  Continue...
        #method = getattr(QtGui.QGraphicsView, event_type)
        #method(self, event)
        return result

    def dispatch_event(self, handler, method_name, event):
        if hasattr(handler, method_name):
            method = getattr(handler, method_name)
            if "mouseMove" not in method_name and False:
                print("Dispatching {} to {}".format(method_name, handler.name))
            result = method(event)
            if result:
                event.accept()
            return result
        else:
            #if 'mouseMove' not in method_name:
            #print("{} event is rejected by {}".format(method_name, handler.name))
            return False

    def keyReleaseEvent(self, event):
        return self.handle_event(event, 'keyReleaseEvent')

    def keyPressEvent(self, event):
        return self.handle_event(event, 'keyPressEvent')

    def mousePressEvent(self, event):
        return self.handle_event(event, 'mousePressEvent')

    def mouseMoveEvent(self, event):
        x, y = self.coords(event, snapped=True)
        pos = event.pos()
        sx, sy = pos.x(), pos.y()
        #print("Move {},{} ({},{})".format(x,y,sx,sy))
        self.mouse_x = x
        self.mouse_y = y
        result = self.handle_event(event, 'mouseMoveEvent')
        return result

    def mouseReleaseEvent(self, event):
        return self.handle_event(event, 'mouseReleaseEvent')

    def mouseDoubleClickEvent(self, event):
        print("View double click")
        return self.handle_event(event, 'mouseDoubleClickEvent')

    def wheelEvent(self, event):
        return self.handle_event(event, 'wheelEvent')

    def setCursor(self, cursor):
        self.viewport().setCursor(cursor)

    # --------------------------------------------------------
    #    Item selections
    # --------------------------------------------------------
    def clearSelections(self):
        # Send a copy of selected_items
        # so we can iterate over it while
        # modifying the original
        self.unselect(list(self.selected_items))

    def select(self, items):
        if not isinstance(items, collections.Iterable):
            items = (items,)

        for item in items:
            item.selected = True
            self.selected_items.append(item)

    def unselect(self, items):
        if not isinstance(items, collections.Iterable):
            items = (items,)

        for item in list(items):
            # Calling the select method will also
            # call the items update() method
            item.selected = False
            self.selected_items.remove(item)

    def selectedItems(self):
        return self.selected_items


    # --------------------------------------------------------
    #    Pan/Zoom Methods
    # --------------------------------------------------------
    def zoom_fit(self):
        """ Sets the zoom so the entire sheet fits in the viewport"""
        if len(self.canvas.items()) == 0:
            scene_rect = self.mapToScene(QtCore.QRect(0,0, self.width(), -1*self.height()))
            scene_rect = self.canvas.sceneRect()
            rect = scene_rect.toRect()
        else:
            rect = self.canvas.itemsBoundingRect().adjusted(-10, -10, 10, 10)
        self.fitInView(QtCore.QRectF(rect), Qt.KeepAspectRatio)

    def zoom(self, x, y=None, center=None):
        """ Zooms (scales) the Canvas by the given ratio.

        The view will be re-centered to 'center' scene coords
        after the zoom operation.  This feature is used by
        the wheel zoom tool.
        """
        if y is None:
            y = x

        # Need to get the current center of the view
        # so we can recenter the view after zooming
        if center is None:
            center = self.mapToScene(self.rect()).boundingRect().center()

        # Move the center to the origin
        self.pan(x=-1 * center.x(), y=-1 * center.y())

        # Now scale
        self.scale(x, y)

        # Then move back
        self.pan(center.x(), center.y())

    def pan(self, x=0, y=0):
        """Pans the Canvas by the x and y values in Scene coordinates.
        """
        self.translate(-1 * x, -1 * y)

    def zoomRect(self, rect):
        """Sets the view to the specified rectangle"""
        self.fitInView(QtCore.QRectF(rect), Qt.KeepAspectRatio)

    # --------------------------------------------------------
    #    Coordinate translations
    # --------------------------------------------------------
    def sceneScale(self):
        """Returns the ratio of scene vectors to view size"""
        tr = self.viewportTransform()
        # m11 is the horizontal scale factor
        # m22 is the vertical scale factor,
        sx, sy = tr.m11(), tr.m22()
        return sx, sy

    def viewPortRect(self):
        """Returns the view area in scene coordinates"""
        return self.mapToScene(self.rect()).boundingRect()

    def coords(self, event, snapped=False):
        '''Helper function to return mouse coordinates
        as a tuple of scene coordinates'''
        point = self.mapToScene(event.pos())

        x = point.x()
        y = point.y()
        if snapped:
            x, y = self.snap_coords(x, y)
        return x, y

    def snap_coords(self, x, y):
        snap = self.snap
        x = round(x / snap) * snap
        y = round(y / snap) * snap
        return x, y

    # --------------------------------------------------------
    #    Background rendering methods
    # --------------------------------------------------------
    def drawBackground(self, painter, rect):
        # Draw the backdrop
        painter.setBrush(QtGui.QBrush(Qt.gray, Qt.SolidPattern))
        #rect = self.canvas.bounds
        coords = rect.getCoords()[::-1]
        if True:
            gradient = QtGui.QLinearGradient(*coords)
            gradient.setColorAt(0, Qt.gray)
            gradient.setColorAt(1, Qt.white)
            painter.setBrush(gradient)
        else:
            painter.setBrush(Qt.gray)
        painter.drawRect(rect)

        # Draw page background
        painter.fillRect(self.canvas.bounds, Qt.white)

        # Grid lines
        if self.grid:
            self.drawGrid(painter=painter, interval=self.grid_interval,
                          x=self.origin.x, y=self.origin.y,
                          color=Qt.gray,
                          rect=self.canvas.bounds,
                          tick_interval=self.tick_interval)

            self.drawDottedGrid(painter, interval=self.dot_interval,
                                rect=self.canvas.bounds,
                                x=self.origin.x, y=self.origin.y)

        # Draw page border
        pen = QtGui.QPen(Qt.black)
        pen.setWidth(2)
        pen.setJoinStyle(Qt.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.transparent)
        painter.drawRect(self.canvas.bounds)

    def drawOrigin(self, painer, x=0, y=0, size=50):
        pass

    def drawGrid(self, painter, x=0, y=0, rect=None, interval=100,
        color=Qt.darkGray, tick_interval=None):

        r = rect
        rect = self.canvas.bounds
        vgrid = View.ticks(x, r.left(), r.right(), interval)
        hgrid = View.ticks(y, r.top(), r.bottom(), interval)

        hlines = [QtCore.QLineF(r.left(), y, r.right(), y) for y in hgrid]
        vlines = [QtCore.QLineF(x, r.bottom(), x, r.top()) for x in vgrid]
        self.grid_lines = hlines, vlines

        color = QtGui.QColor(color)
        color.setAlphaF(0.5)
        pen = QtGui.QPen(color)
        pen.setWidth(0)
        painter.setPen(pen)

        painter.drawLines(hlines)
        painter.drawLines(vlines)

        if tick_interval is not None:
            tick_size = 0.05 * tick_interval
            vticks = View.ticks(x, r.left(), r.right(), tick_interval)
            hticks = View.ticks(y, r.top(), r.bottom(), tick_interval)

            htick_lines = [QtCore.QLineF(x - tick_size, y, x + tick_size, y)
                for y in hticks for x in vgrid]
            vtick_lines = [QtCore.QLineF(x, y - tick_size, x, y + tick_size)
                for y in hgrid for x in vticks]
            self.tick_lines = htick_lines, vtick_lines
            painter.drawLines(htick_lines)
            painter.drawLines(vtick_lines)

    def drawDottedGrid(self, painter, x=0, y=0, rect=None, interval=10,
        width=1, color=Qt.gray):
        r = rect
        vpoints = View.ticks(x, r.left(), r.right(), interval)
        hpoints = View.ticks(y, r.top(), r.bottom(), interval)
        self.points = [QtCore.QPoint(x, y) for x in vpoints for y in hpoints]

        color = QtGui.QColor(color)
        color.setAlphaF(0.5)
        pen = QtGui.QPen(color)
        pen.setWidth(0)
        painter.setPen(pen)
        painter.drawPoints(*self.points)

    def drawForeground(self, painter, rect):
        if self.selection_box is not None:
            pen = QtGui.QPen(Qt.blue)
            color = QtGui.QColor(Qt.blue)
            color.setAlphaF(0.5)
            brush = QtGui.QBrush(color)
            painter.setPen(pen)
            painter.setBrush(brush)
            painter.drawRect(self.selection_box)

    def updateSelectionBox(self, rect):
        self.selection_box = rect
        self.viewport().update()

    def hideSelectionBox(self):
        self.selection_box = None
        self.viewport().update()
        self.update

    # ----------------------------------------------------------------
    #  Ticks:  Helper function to return grid coordinates
    # ----------------------------------------------------------------
    @staticmethod
    def ticks(x0, min_value, max_value, interval):
        sign = np.sign([x0, min_value, max_value])
        sign[sign == 0] = 1
        # Add a small amount to the end point so it is included (interval/10)
        left = np.arange(x0, min_value + (interval / 10), sign[0] * sign[1] * interval)
        right = np.arange(x0, max_value + (interval / 10), sign[0] * sign[2] * interval)
        values = np.unique(np.append(left, right))
        values = values[values >= min_value]
        values = values[values <= max_value]
        return values

    @property
    def bindings(self):
        return self.canvas.bindings

    def update(self):
        items = self.items()
        for item in items:
            item.update()