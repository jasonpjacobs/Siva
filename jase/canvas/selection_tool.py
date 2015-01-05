"""

"""
from ..qt_bindings import QtCore, Qt


from .tools import Tool
from .items import Item
from .styles import ItemStyle

class DimSelectionStylizer(ItemStyle):
    """ Renders selected objects opaque,
    and unselected objects at half transparency
    """
    def apply(self, style, obj):
        if not obj.selected:
            color = style.pen.color()
            alpha = color.alphaF()
            alpha = alpha * 0.5
            color.setAlphaF(alpha)
            style.pen_color = color
            color = style.brush.color()
            alpha = color.alphaF()
            alpha = alpha * 0.5
            color.setAlphaF(alpha)
            style.brush_color = color

        return style

class SelectionTool(Tool):
    def __init__(self, parent, style=None):
        super(SelectionTool, self).__init__(parent=parent)
        self.name = "Selection Tool"
        self.state = None
        self.selection_candidates = []

        # Load key bindings
        # self.zoom_fit_key = self.parent.bindings["Select"]
        self.select_key = Qt.Key_S
        self.cancel_key = Qt.Key_Escape
        self.multiple_selection_key_modifier = Qt.Key_Shift
        self.box_selection_button = Qt.LeftButton

        # For box selections
        self.start = None
        self.end = None

        if style is None:
            self.style_map["active selection"] = DimSelectionStylizer()

    def keyReleaseEvent(self, event):
        if event.key() == self.select_key:
            self.state = "selecting"
            self.view_mode = "active selection"
            self.parent.activateTool(self)
            if self.style_map:
                self.parent.update()
            return True
        elif event.key() == self.cancel_key:
            self.cancel()
            return True
        elif event.key() == Qt.Key_A:
            # For debug...
            print("Selected items:")
            print(self.parent.selected_items)
            return True
        return False

    def mousePressEvent(self, event):
        # Start a selection box
        if self.state == "selecting" and (
                    event.buttons() & self.box_selection_button):
            if self.start is None:
                self.start = self.parent.mapToScene(event.pos())
            return True

    def mouseMoveEvent(self, event):
        """Highlight items that will be selected
        if the mouse is clicked.
        """
        if self.state == "selecting":

            # If the mouse button is pressed, we are
            # starting a mouse drag
            if event.buttons() & self.box_selection_button:
                self.state = "box selection"

            # Now see if any items are under the cursor
            # and highlight them
            item = self.parent.itemAt(event.pos())
            if item is not None:
                item.outline = True
                self.selection_candidates.append(item)
                item.update()
                print("Item bbox ", item.boundingRect(), item.shape(), " @ ", event.pos())
                return True
            else:
                # Deselect any previous selection candidates
                for item in self.selection_candidates:
                    #assert isinstance(item, Item)
                    item.outline = False
                self.selection_candidates = []
                return False
        elif self.state == "box selection" and (
                    event.buttons() & self.box_selection_button):
            # A mouse drag is happening.  Update the selection box.
            self.end = self.parent.mapToScene(event.pos())

            # Update the selection box
            if self.start is not None:
                self.parent.updateSelectionBox(
                    QtCore.QRectF(self.start, self.end))

            # Highlight all of the items in the selection area
            items = self.parent.scene().items(QtCore.QRectF(self.start, self.end), Qt.ContainsItemShape)

            # Items that are newly selected
            new = [item for item in items if item not in self.selection_candidates]

            # Items that were previous selected, but now are outside the selection box
            old = [item for item in self.selection_candidates if item not in items]

            # Highlight the new ones
            for item in new:
                item.outline = True
                self.selection_candidates.append(item)

            # And unhighlight the old one
            for item in old:
                item.outline = False
                self.selection_candidates.remove(item)

            return True
        return False

    def mouseReleaseEvent(self, event):
        if self.state == "selecting":
            item = self.parent.itemAt(event.pos())
            if item is not None:
                self.handle_items((item,), event)
            else:
                # A click with no item underneath should clear the selections
                if not event.modifiers() == Qt.ShiftModifier:
                    # Clear any previous selections
                    self.parent.clearSelections()
            return True

        elif self.state == "box selection":
            self.end = self.parent.mapToScene(event.pos())
            items = self.parent.scene().items(QtCore.QRectF(self.start, self.end), Qt.ContainsItemShape)
            self.handle_items(items, event)

            # Box selection complete, restore
            # the state to "selecting"
            self.parent.hideSelectionBox()
            self.state = "selecting"
            self.start = None
            self.end = None
            return True
        else:
            return False

    def handle_items(self, items, event):
        if not event.modifiers() == Qt.ShiftModifier:
            # Clear any previous selections
            self.parent.clearSelections()
        for item in items:
            if item is not None and item.selectable:
                # Toggle the item's selection via the View
                # so the view's selected set stays in sync
                if item.selected is False:
                    self.parent.select(item)
                else:
                    self.parent.unselect(item)
                item.update()

    def cancel(self):
        self.state = None
        for item in self.selection_candidates:
            item.outline = False

        self.parent.clearSelections()
        self.selection_candidates = []
        self.parent.deactivateTool(self)

        self.start = None
        self.end = None
        self.view_mode = None
        if self.style_map:
            self.parent.update()

    def get_style(self):
        style = self.style_map.get(self.view_mode, None)
        return style