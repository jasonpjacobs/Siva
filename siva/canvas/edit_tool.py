"""

"""

from ..qt_bindings import QtCore


from .tools import Tool, ToolState, stateful_class
from .resize_handle import ResizeHandle

import pdb

@stateful_class
class EditTool(Tool):
    """ Tool to edit Item's via control points on the Canvas

    """

    class IdleState(ToolState):
        def mouseMoveEvent(self, event):
            item = self.tool.parent.itemAt(event.pos())
            if item is not None and issubclass(item.__class__, ResizeHandle):
                self.tool.parent.setCursor(item.cursor())
                item.highlight = True
                return True

        def mousePressEvent(self, event):
            item = self.tool.parent.itemAt(event.pos())
            if item is not None and issubclass(item.__class__, ResizeHandle):
                # Remember where the drag was started
                # To get scene coords, we ask map the ControlPoint's position
                # relative to the parent to the scene
                self.tool.start = item.parent.mapToScene(item.pos())
                self.tool.handle = item
                self.tool.state = self.tool.ReadyToDrag
                return True


    class ReadyToDragState(ToolState):
        def mouseMoveEvent(self, event):
            coords = self.tool.coords(event)
            start = self.tool.start

            delta = coords - start
            pos = coords - delta
            handle = self.tool.handle
            item_pos = handle.parent.mapFromScene(pos)
            self.tool.start = coords
            handle.parent.prepareGeometryChange()
            if handle.moveable:
                handle.setPos(handle.parent.mapFromScene(pos))
            if handle.callback is not None:
                handle.callback(pos=item_pos, coords=handle.parent.mapFromScene(coords))
            return True

        def mouseReleaseEvent(self, event):
            self.tool.item = None
            self.tool.start = None
            self.tool.state = self.tool.Idle

    def __init__(self, parent, *args, **kwargs):
        super(EditTool, self).__init__(parent, *args, **kwargs)
        self.name = "Edit Tool"
        self.snap = True

        # Tool state instances
        self.Idle = EditTool.IdleState(tool=self, view=parent)
        self.ReadyToDrag = EditTool.ReadyToDragState(tool=self, view=parent)

        self.state = self.Idle
        # For development
        self.parent.activateTool(self)
