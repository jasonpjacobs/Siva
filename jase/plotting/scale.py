from ..qt_bindings import QtGui, QtCore, Qt, Signal

import math
import pdb
import numpy as np
from numbers import Number

def nice_num(x, round=False):
    """Finds a 'nice' number approximately equal to x.

    Python implementation of Paul Heckbert's algorithm
    published in Graphics Gem (vol I),
    "Nice Numbers for Graph Labels", pp 61-63

    http://tog.acm.org/resources/GraphicsGems/gems/Label.c
    """
    if x == 0.0:
        return 1
    try:
        expv = math.floor(math.log10(x))    # Exponent of X
        f = x/math.pow(10, expv)            # Fractional part of X
    except ValueError as e:
        print("Error with nice_num({})".format(x), e)
        pdb.set_trace()
        raise

    if round:
        nice_numbers = {1.5:1, 3.:2., 7.:5.}
    else:
        nice_numbers = {1.:1., 2.:2., 5.:5.}

    nf = None   #nice, rounded fraction
    if round:
        if f < 1.5:
            nf = 1.
        elif f < 3.:
            nf = 2.
        elif f < 7.:
            nf = 5.
        else:
            nf = 10.
    else:
        if f < 1.:
            nf = 1.
        elif f < 2.:
            nf = 2.
        elif f < 5.:
            nf = 5.
        else:
            nf = 10.

    num = nf*math.pow(10, expv)
    return num

class Scale(QtCore.QObject):
    value_changed = Signal()

    def __init__(self, plot, axis="x", domain=None):
        """
        """

        super().__init__()

        self.plot = plot
        self.scene = plot.scene
        self.axis = axis
        self.domain = domain
        self.scale = 1.0
        self.offset = 0

        self.min = None
        self.max = None

    @property
    def range(self):
        x,y = self.scene_visible_range()
        if self.axis == "x":
            return x
        else:
            return y

    @range.setter
    def range(self):
        pass

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        self.value_changed.emit()

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value
        self.value_changed.emit()

    def zoom(self, value):
        self.scale *= value

    def pan(self, value, mode="absolute"):
        if mode == "relative":
            step = (self.range[1] - self.range[0])*value
        else:
            step = value
        screen_offset = self.scale*step
        self.offset += screen_offset


    def ticks(self, N=10, range=None):
        if range is None:
            range = self.range

        xmin, xmax = min(range), max(range)
        x_range = nice_num(xmax - xmin, round=False)
        d = step = nice_num(x_range/(N-1), round=True)
        start = math.floor(xmin/d)*d
        stop = math.ceil(xmax/d)*d

        # Generate the ticks
        ticks = np.arange(start, stop, step)
        return ticks

    def to_screen(self, values):
        """Converts data coordinates to screen coordinates, relative to the plot origin
        """
        if self.axis == "x":
            scale = self.scale
            b = self.offset
        else:
            scale = self.scale
            b = self.offset

        if isinstance(values, Number):
            return scale*values + b
        else:
            return [scale*x + b for x in values]

    def to_data(self, values):
        """Converts screen coordinates to data coordinates
        """
        if self.axis == "x":
            scale = self.scale
            b = self.offset
        else:
            scale = self.scale
            b = self.offset
        if isinstance(values, Number):
            return (values - b)/scale
        return [(x - b)/scale for x in values]

    @property
    def pixel(self):
        """Calculates the size of the view's pixel in scene coordinates
        """
        matrix = self.plot.transform()
        if self.axis == "x":
            scale = matrix.m11()
        else:
            scale = matrix.m22()
        return scale

    def scene_visible_range(self):
        """
        Returns the visible ranges of the scene visible in the plot in data coordinates
        """
        rect = self.plot.visibleRegion().boundingRect()
        rect = self.plot.mapToScene(rect).boundingRect()
        ll = rect.bottomLeft()
        ur = rect.topRight()

        x = min(ll.x(), ur.x()), max(ll.x(), ur.x())
        y = -1*max(ll.y(), ur.y()), -1*min(ll.y(), ur.y())
        pdb.set_trace()
        return (self.to_data(x), self.to_data(y))


    def fit(self, v1=None, v2=None, s1=None, s2=None):
        """ Changes the scale and offset so the two data space values v1, v2 fit within the view
        :param v1:
        :param v2:
        :return:
        """
        # Get the plot area in screen coordinates
        assert s1 is not None
        assert s2 is not None

        s_range = (s1, s2)

        # Compute the data range
        if v1 is not None and v2 is not None:
            dmin = min(v1, v2)
            dmax = max(v1, v2)
        else:
            dmin = self.min
            dmax = self.max

        # Linear scale for now
        if (dmax - dmin) <= 0:
            dmax = 1
            dmin = 0

        # Scale is pixels/data unit
        self.scale = (max(s_range) - min(s_range))/(dmax - dmin)
        self.scale *= -1 if self.axis == "y" else 1.0

        if self.axis == "x":
            self.offset = min(s_range) - self.scale*dmin
        else:
            self.offset = min(s_range) - self.scale*dmax

        self.value_changed.emit()

    def update_range(self, data):
        try:
            min = np.min(data)
            max = np.max(data)
        except TypeError:
            # Handle cases such as state plots, where
            # Y values are non numeric
            min = 0
            max = 1

        if self.min is not None:
            self.min = min if min < self.min else self.min
        else:
            self.min = min

        if self.max is not None:
            self.max = max if max > self.max else self.max
        else:
            self.max = max

        self.value_changed.emit()

    def draw_axis(self, painter, rect, side="bottom", plot=None, padding=20,
                  color=None, width=4, style=Qt.SolidLine, pen=None, margins=None, labels=True):

        if color is None:
            color = QtGui.QColor(Qt.black)

        if pen is None:
            pen = QtGui.QPen(color)

        pen.setWidthF(width/self.pixel)
        pen.setStyle(style)
        painter.setPen(pen)

        if side in ("bottom", "top"):
            if side == "bottom":
                painter.drawLine(QtCore.QLineF(rect.bottomLeft(), rect.bottomRight()))
            else:
                painter.drawLine(QtCore.QLineF(rect.topLeft(), rect.topRight()))
            x_min, x_max = self.to_data((rect.left(), rect.right()))
            major_ticks =  [x for x in self.ticks(N=10, range=(x_min,x_max)) if x >= x_min and x <= x_max]
            minor_ticks =  [x for x in self.ticks(N=50, range=(x_min, x_max)) if x >= x_min and x <= x_max]
        elif side in ("left", "right"):
            if side == "left":
                painter.drawLine(QtCore.QLineF(rect.topLeft(), rect.bottomLeft()))
            else:
                painter.drawLine(QtCore.QLineF(rect.topRight(), rect.bottomRight()))
            y_min, y_max = self.to_data((rect.top(), rect.bottom()))
            major_ticks =  [y for y in self.ticks(N=10, range=(y_min, y_max)) if y <= y_min and y >= y_max]
            minor_ticks =  [y for y in self.ticks(N=50, range=(y_min, y_max)) if y <= y_min and y >= y_max]


        self.draw_ticks(painter, rect,  ticks=major_ticks,  width=2, side=side, padding=padding)
        self.draw_ticks(painter, rect,  ticks=minor_ticks,  tick_size=5, width=0, side=side, padding=padding)
        if labels:
            self.draw_tick_labels(painter, rect, ticks=major_ticks, side=side, margins=margins, padding=padding)

    def draw_ticks(self, painter, rect, ticks, tick_size=10, side="top",
                   pen=None, style=Qt.SolidLine, width=2, color=None, padding=0):
        tick_size = tick_size / self.pixel
        ticks = self.to_screen(ticks)
        if side == "bottom":
            y = rect.bottom()
            tick_lines = [QtCore.QLineF(x, y - tick_size, x, y) for x in ticks if x >= rect.left() and x <= rect.right()]
        elif side == "top":
            y = rect.top()
            tick_lines = [QtCore.QLineF(x, y + tick_size, x, y) for x in ticks]
        elif side == "left":
            x = rect.left()
            tick_lines = [QtCore.QLineF(x, y, x + tick_size, y)
                for y in ticks]
        else:
            x = rect.right()
            tick_lines = [QtCore.QLineF(x, y - tick_size/2, x, y + tick_size/2)
                for x in ticks]

        if color is None:
            color = QtGui.QColor(Qt.black)

        if pen is None:
            pen = QtGui.QPen(color)

        pen.setWidthF(width/ self.pixel)
        pen.setStyle(style)
        painter.setPen(pen)
        painter.drawLines(tick_lines)

    def draw_tick_labels(self, painter, rect, ticks=None, side="bottom", margins=None, padding=0):
        font = QtGui.QFont('Helvetica')
        info = QtGui.QFontInfo(font)
        font.setPixelSize(12)
        painter.setFont(font)

        fm = QtGui.QFontMetricsF(font)

        if side == "bottom":
            for t in ticks:
                txt ="{:6.3g}".format(t)
                w = fm.width(txt)
                h = 30    # Covert pixels to screen space
                x = self.to_screen(t)
                y = rect.bottom()
                painter.drawText(QtCore.QRectF(x-w/2, y, w, h), Qt.AlignCenter, txt)
        elif side == "top":
            for t in ticks:
                txt ="{:6.3g}".format(t)
                w = fm.width(txt)
                h = margins["top"]
                x = self.to_screen(t)
                y = rect.top()
                painter.drawText(QtCore.QRectF(x, y-h, w, h), Qt.AlignCenter | Qt.AlignBottom, txt)
        elif side == "left":
            for t in ticks:
                txt ="{:6.3g}".format(t)
                w = margins['left']
                h = fm.height()
                y = self.to_screen(t)
                x = (rect.left()) - w - 4 # 4 -->  Margin to axis
                painter.drawText( QtCore.QRectF(x, y - h/2, w, h), Qt.AlignVCenter | Qt.AlignRight, txt)
        elif side == "right":
            for t in ticks:
                txt ="{:6.3g}".format(t)
                w = margins['right']
                h = fm.height()
                y = self.to_screen(t)
                x = rect.right() + 4
                painter.drawText( QtCore.QRectF(x, y - h/2, w, h), Qt.AlignVCenter | Qt.AlignLeft, txt)


    def draw_grid(self, painter, rect, pen=None, style=Qt.DashLine, width=0, color=None):
        if self.axis == "x":
            range = self.to_data((rect.left(), rect.right()))
        else:
            range = self.to_data((rect.top(), rect.bottom()))
        d_ticks = self.ticks(N=10, range=range)
        s_ticks = self.to_screen(d_ticks)
        r = rect

        if self.axis == "y":
            lines = [QtCore.QLineF(r.left(), y, r.right(), y) for y in s_ticks]
        else:
            lines = [QtCore.QLineF(x, r.bottom(), x, r.top()) for x in s_ticks]

        if color is None:
            color = QtGui.QColor(50, 50, 50, 50)
        if pen is None:
            pen = QtGui.QPen(color)

        pen.setWidthF(width)
        pen.setStyle(style)
        painter.setPen(pen)

        painter.drawLines(lines)
