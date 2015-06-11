"""

"""

from ..qt_bindings import QtCore, Qt

from .tools import Tool


class ZoomTool(Tool):
    """ Implements two modes of zooming via the mouse.

    The first is via a zoom box.  The user draws a
    box on the canvas that becomes the extent of the
    view.

    The second is via mouse movement, where
    moving the mouse up increase the zoom level
    and moving it down decreases it.
    """
    def __init__(self, *args, **kwargs):
        super(ZoomTool, self).__init__(*args, **kwargs)
        self.name = "Zoom Tool"
        self.mode = None

        # Load key/mouse bindings
        self.zoom_fit_key = self.parent.bindings["Zoom Fit"]
        self.zoom_box_key = self.parent.bindings["Zoom Box"]
        self.box_zoom_button = self.parent.bindings["Box Zoom Button"]
        self.mouse_zoom_button = self.parent.bindings.get("Mouse Zoom Button",
                                                              Qt.RightButton)

    def wheelEvent(self, event):
        center = self.parent.mapToScene(event.pos())
        if event.orientation() == Qt.Vertical:
            d = event.delta() / 8
            ratio = abs((d / 15.0) * 1.25)
            if d < 0:
                scale = 1 / ratio
            else:
                scale = ratio
            self.parent.zoom(scale, center=center)
            return True

    def keyPressEvent(self, event):
        if event.key() == self.zoom_fit_key:
            self.parent.zoom_fit()
            return True
        if event.key() == self.zoom_box_key:
            self.mode = "box zoom"
            self.start = None
            self.parent.activateTool(self)
            return True
        if event.key() == Qt.Key_Escape:
            self.mode = None
            self.parent.hideSelectionBox()
            # Let the cancel request propagate to other tools
            return False
        return False

    def mousePressEvent(self, event):
        if self.mode == "box zoom" and (
        event.buttons() & self.box_zoom_button):
            if self.start is None:
                self.start = self.parent.mapToScene(event.pos())
            return True
        elif event.buttons() & self.mouse_zoom_button:
            # A mouse zoom is starting
            self.mode = "mouse zoom"
            self.start = event.pos()
        else:
            return False

    def mouseReleaseEvent(self, event):
        if self.mode == "box zoom":
            # Mouse drag complete.  Implement the zoom
            # and deactivate the tool
            if self.start is not None:
                self.end = self.parent.mapToScene(event.pos())
                # Implement the zoom
                self.parent.zoomRect(QtCore.QRectF(self.start, self.end))
                self.parent.hideSelectionBox()
                self.parent.deactivateTool(self)
                self.mode = None
            return True
        if self.mode == "mouse zoom":
            self.mode = None
        else:
            return False

    def mouseMoveEvent(self, event):
        if self.mode == "box zoom" and (
        event.buttons() & self.box_zoom_button):
            # A mouse drag is happening.  Update the selection box.
            self.end = self.parent.mapToScene(event.pos())
            if self.start is not None:
                self.parent.updateSelectionBox(
                    QtCore.QRectF(self.start, self.end))
            return True
        elif self.mode == "mouse zoom" and (
        event.buttons() & self.mouse_zoom_button):

            center = self.parent.mapToScene(self.start)
            if event.pos().y() < self.start.y():
                self.parent.zoom(x=1.1, center=center)
            else:
                self.parent.zoom(x=0.9, center=center)
        else:
            return False

