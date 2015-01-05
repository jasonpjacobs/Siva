__author__ = 'Jase'
from ..qt_bindings import QtGui, QtCore, Qt
from .canvas import Canvas

class CanvasWidget(QtGui.QWidget):
    """ A widget and layout to hold the Canvas object """
    def __init__(self, canvas=None, *args, **kwargs):
        super().__init__()

        if canvas is not None:
            self.canvas = canvas
        else:
            self.canvas = Canvas(*args, **kwargs)

        # Create a layout and add the Canvas's view to the layout
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.canvas._view)
        self.setLayout(layout)


