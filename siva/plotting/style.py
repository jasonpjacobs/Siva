"""

"""

from ..qt_bindings import QtGui, QtCore, Qt



class Mapper:
    """Maps data points to colors, or numerical values
    """
    pass

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

class Style:
    """A class to store style attributes (color, width, size) for brushes, pens and fonts.
    """
    def __init__(self, **kwargs):
        if "line_color" in kwargs:
            self.pen_color = kwargs["line_color"]
        elif "line" in kwargs:
            self.pen_color = kwargs["line"]
        elif "color" in kwargs:
            self.pen_color = kwargs["color"]
        else:
            self.pen_color = Qt.black

        if "line_width" in kwargs:
            self.pen_width = kwargs["line_width"]
        elif "width" in kwargs:
            self.pen_width = kwargs["width"]
        else:
            self.pen_width = 0

        if "fill_color" in kwargs:
            self.brush_color = kwargs["fill_color"]
        elif "fill" in kwargs:
            self.brush_color = kwargs["fill"]
        elif "color" in kwargs:
            self.brush_color = kwargs["color"]
        else:
            self.brush_color = Qt.transparent

        if 'antialias' in kwargs:
            self.antialias = True
        else:
            self.antialias = None


        if 'align' in kwargs:
            self.alignment = kwargs['align']
        else:
            self.alignment = Qt.AlignCenter|Qt.AlignHCenter


    def configure(self, painter):
        pen = brush = None
        if self.pen_color is not None:
            pen = QtGui.QPen(QtGui.QColor(self.pen_color))

        if pen and self.pen_width is not None:
            pen.setWidthF(self.pen_width)
        if pen:
            painter.setPen(pen)
        else:
            painter.setPen(Qt.NoPen)

        if self.brush_color is not None:
            brush = QtGui.QBrush(QtGui.QColor(self.brush_color))
            painter.setBrush(brush)

        if self.antialias:
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
        return painter