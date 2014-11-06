from jcanvas.canvas_widget import CanvasWidget
from PySide import QtCore

class SchematicEditor(CanvasWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas._view.zoomRect(QtCore.QRect(0,0, self.canvas.width, self.canvas.height))