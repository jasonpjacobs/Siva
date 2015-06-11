"""

"""

from ..qt_bindings import QtCore, Qt


from .tools import Tool

class PanTool(Tool):
    def __init__(self, *args, **kwargs):
        super(PanTool, self).__init__(*args, **kwargs)
        self.name = "Pan Tool"

        # Load key bindings
        self.left_key = self.parent.bindings["Pan Left"]
        self.right_key = self.parent.bindings["Pan Right"]
        self.up_key = self.parent.bindings["Pan Up"]
        self.down_key = self.parent.bindings["Pan Down"]
        self.mouse_pan_button = self.parent.bindings["Mouse Pan Button"]

        # Initial state
        self.active = False

    def mousePressEvent(self, event):
        if (event.buttons() & self.mouse_pan_button):
            self.parent.setCursor(Qt.ClosedHandCursor)
            self.active = True
            self.start = event.pos()

            # Don't consume the mouse click, since it may have been intended
            # for items underneath the cursor
            return False
        else:
            return False

    def mouseMoveEvent(self, event):
        if self.active and (
        event.buttons() & self.mouse_pan_button):
            end = event.pos()
            delta = self.start - end
            hsb = self.parent.horizontalScrollBar()
            vsb = self.parent.verticalScrollBar()
            hsb.setValue(hsb.value() + delta.x())
            vsb.setValue(vsb.value() + delta.y())
            self.start = end
            return True
        else:
            return False

    def mouseReleaseEvent(self, event):
        if self.active:
            self.active = False
            self.parent.restoreCursor()
            return True
        else:
            return False

    def keyPressEvent(self, event):
        if event.key() == self.left_key:
            self.parent.pan(-100, 0)
            return True

        if event.key() == self.right_key:
            print("Pan right")
            self.parent.pan(100, 0.0)
            return True

        if event.key() == self.up_key:
            self.parent.pan(0, 100)
            return True

        if event.key() == self.down_key:
            self.parent.pan(0, -100.0)
            return True
        return False

