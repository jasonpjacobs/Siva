""" Contains class definitions for the various types of plot item, including simple line plots, logic plots,
state plots, bar plots, etc.

"""

from ..qt_bindings import QtGui, QtCore, Qt

from .style import Style

import numpy as np
import pdb

class Annotation(QtGui.QGraphicsItem):
    """ A text object drawn as part of the plots at a specific location in data space.  Used, for example,
    by the StatePlot to label the state names.
    """
    def __init__(self, txt="", font=None, rect=None, style=None):
        self.txt = txt
        self.font = font
        self.rect = rect
        self.style = style

    def paint(self, painter):
        painter.save()
        self.style.configure(painter)
        painter.drawText(self.rect, self.style.alignment, self.txt)
        painter.restore()

class PlotItem(QtGui.QGraphicsItem):
    def __init__(self,  obj=None, x=None, y=None, markers=None, plot=None, parent=None, n=0, style=None, domain=None,
        **kwargs):
        super().__init__(parent=parent)

        args = (obj is not None, x is not None, y is not None)
        if args == (True, True, False):
            x = np.array(obj) # The 1st argument passed to *this* method
            y = np.array(x)   # The 2nd argument passed to *this* method
        elif args == (False, True, True):
            x = np.array(x)
            y = np.array(y)
        elif args == (True, False, False) and hasattr(obj,'x'):
            x = obj.x
            y = obj.y
        else:
            raise ValueError("Incorrect args provided to plot function: {}, {}, {}".format(obj, x, y))

        assert(len(x) >= len(y))
        assert(len(x) <= len(y) + 1)

        self.name = ""
        self.data = (x,y)
        self.n = n

        self._bounding_rect = None

        # Top level plot where this item is rendered
        self.plot = plot

        # A collection of QPainterPaths, and the Styles objects used to paint them
        self.painter_paths = []
        self.annotations = []
        self.style = style

        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setAcceptsHoverEvents(True)

        self.plot_type = "PlotItem"

        if style is None:
            import random

            if 'color' not in kwargs:
                rgb = (255*random.random(), 255*random.random(), 255*random.random())
                color = QtGui.QColor(*rgb)
                kwargs['line_color'] = color
            self.style = Style(antialias=True, width=1, **kwargs)

    def boundingRect(self, *args, **kwargs):
        x = self.data[0]
        y = self.data[1]
        x = self.plot.x_scale.to_screen(x)
        y = self.plot.y_scale.to_screen(y)
        if self._bounding_rect is None or True:
            self._bounding_rect = QtCore.QRectF(np.min(x), -1*np.min(y), np.ptp(x), np.ptp(y))
        return self._bounding_rect

    def create_painter_paths(self):
        raise NotImplementedError("Must be reimplemented in child classes")

    def paint(self, painter, option, widget):
        if not self.painter_paths or True:
            self.create_painter_paths()

        for path, style in self.painter_paths:
            painter.setClipRect(self.plot.plot_rect)
            style.configure(painter)
            painter.drawPath(path)

        for txt_item in self.annotations:
            txt_item.paint(painter)

    def repr(self):
        return self.plot_type

class LinePlot(PlotItem):
    def __init__(self,  obj=None, x=None, y=None, markers=None, parent=None, plot=None, **kwargs):
        super().__init__(parent=parent, obj=obj, x=x, y=y, markers=markers, plot=plot, **kwargs)
        self.plot_type = "LinePlot"

    def create_painter_paths(self):
        self.painter_paths = []
        path = QtGui.QPainterPath()

        x = self.plot.x_scale.to_screen(self.data[0])
        y = self.plot.y_scale.to_screen(self.data[1])

        path.moveTo(x[0],y[0])
        for x,y in zip(x[1:], y[1:]):
            path.lineTo(x,y)

        self.painter_paths.append((path, self.style))

        # Create a path for use with the shape() method (hit detection, etc)
        self.path = QtGui.QPainterPath()
        for path, style in self.painter_paths:
            self.path.addPath(path)
        return

    def boundingRect(self, *args, **kwargs):
        #TODO:  Correctly cache path, based on scale and offset
        if not self.painter_paths:
            self.create_painter_paths()

        rect = QtCore.QRectF()
        for path, style in self.painter_paths:
            rect = rect.united(path.boundingRect())
        return rect


class BarPlot(PlotItem):
    def create_painter_paths(self):
        path = QtGui.QPainterPath()
        self.painter_paths = []

        x = self.plot.x_scale.to_screen(self.data[0])
        y = self.plot.y_scale.to_screen(self.data[1])
        y0 = self.plot.y_scale.to_screen(0)
        w = 5
        #path.moveTo(x[0] - w/2, 0)
        for dx,dy in zip(x[1:], y[1:]):
            pass
            #path.addRect(dx-w/2, y0, w, dy)

        path.moveTo(x[0] - w/2, y0)
        for dx,dy in zip(x[1:], y[1:]):
            path.addRect(dx-w/2, y0, w, dy - y0)
        self.painter_paths.append( (path, Style(line_color='black', fill_color='blue', pen_width=0)))
        return

class StemPlot(PlotItem):
    def create_painter_paths(self):
        path = QtGui.QPainterPath()
        y = -1*self.data[1]
        x = self.data[0]
        for x,y in zip(x[1:], y[1:]):
            path.lineTo(x,y)

        self.path = path
        return path


class X(int):
    pass

class Z(int):
    pass

class LogicPlot(PlotItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.h = 20

    def create_painter_paths(self):
        self.painter_paths = []
        view = self.plot.plot_rect

        x_vals = self.plot.x_scale.to_screen(self.data[0])
        y_vals = self.data[1]
        y0 = self.plot.y_scale.to_screen(0)

        font = QtGui.QFont()
        fm = QtGui.QFontMetricsF(font)
        w_txt = fm.width('X')

        h = self.h
        rects_path = QtGui.QPainterPath()
        prev = None
        for i in range(len(y_vals)):
            x1 = x_vals[i]
            y_val = y_vals[i]
            if len(x_vals) > i+1:
                x2 = x_vals[i+1]
            else:
                x2 = view.right() + 1

            # Skip if the interval is not in the view
            if x1 > view.right():
                continue

            # Check for clipping
            if x2 < view.left():
                continue
            if x1 > view.right():
                continue
            path = QtGui.QPainterPath()

            x = x_vals[i]
            points = []
            if prev is not None:
                points.append(prev)

            if y_val == 0:
                y = 0
            elif y_val == 1:
                y = h
            elif y_val == 2: # X
                y = h
            elif y_val == 3: # Z
                y = h/2

            points.append(QtCore.QPointF(x1,y0 - y))
            points.append(QtCore.QPointF(x2,y0 - y))

            if y_val != 3:
                rects_path.addRect(x, y0 - y, x2 - x1, y)

            path.moveTo(points[0])
            for p in points[1:]:
                path.lineTo(p)

            self.painter_paths.append((path, Style(line_color='black', fill_color=None, pen_width=1)))
            #painter.strokePath(path, QtGui.QPen())

            prev = points[-1]

        self.painter_paths.append((rects_path, Style(line_color=None, fill_color=QtGui.QColor(0,0,100,100))))

    def boundingRect(self, *args, **kwargs):
        x = self.data[0]
        x = self.plot.x_scale.to_screen(x)

        y = np.array([self.plot.y_scale.to_screen(0), self.h])

        if self._bounding_rect is None or True:
            self._bounding_rect = QtCore.QRectF(np.min(x), -1*np.min(y), np.ptp(x), np.ptp(y))
        return self._bounding_rect

class StatePlot(PlotItem):
    def create_painter_paths(self):
        self.painter_paths = []
        view = self.plot.plot_rect

        x_vals = self.plot.x_scale.to_screen(self.data[0])
        y_vals = self.data[1]
        y0 = self.plot.y_scale.to_screen(0)

        font = QtGui.QFont()
        fm = QtGui.QFontMetricsF(font)

        h = 20
        dx=5

        self.annotations = []

        for i in range(len(y_vals)):
            x1 = x_vals[i]
            txt = y_vals[i]
            if len(x_vals) > i+1:
                x2 = x_vals[i+1]
            else:
                x2 = view.right() + 1

            # Skip if the interval is not in the view
            if x1 > view.right():
                continue

            # Check for clipping
            if x2 < view.left():
                continue
            elif x1 < view.left():
                left_clipped = True
                x1 = view.left()
            else:
                left_clipped = False

            if x1 > view.right():
                print("Skipping", i)
                continue
            elif x2 > view.right():
                right_clipped = True
                x2 = view.right()
            else:
                right_clipped = False

            state_path = QtGui.QPainterPath()

            # Bottom left
            state_path.moveTo( QtCore.QPointF(x1+dx, y0))

            # Middle left
            state_path.lineTo(QtCore.QPointF(x1, y0 - h/2))

            # Upper left
            state_path.lineTo(QtCore.QPointF(x1 + dx, y0 - h))

            # Upper right
            if right_clipped:
                state_path.lineTo(QtCore.QPointF(x2, y0 - h))
            else:
                state_path.lineTo(QtCore.QPointF(x2 - dx, y0 - h))

            # Middle right
            state_path.lineTo(QtCore.QPointF(x2, y0 - h/2))

            # Bottom right
            if right_clipped:
                state_path.lineTo(QtCore.QPointF(x2, y0))
            else:
                state_path.lineTo(QtCore.QPointF(x2 - dx, y0))

            # Back to the lower left
            state_path.lineTo( QtCore.QPointF(x1+dx, y0))
            self.painter_paths.append( (state_path, Style(fill_color='yellow')))

            # Txt annotation of the state name
            rect =  QtCore.QRectF(x1 + dx, y0-h, x2-x1, h)
            annotation = Annotation(txt=txt, font=font, rect=rect, style=Style(line_color='black', alignment=Qt.AlignHCenter))
            self.annotations.append(annotation)

    def create_painter_paths2(self):
        path = QtGui.QPainterPath()

        x_vals = self.plot.x_scale.to_screen(self.data[0])
        y_vals = self.plot.y_scale.to_screen(40*np.arange(len(self.data[1])))

        y0 = self.plot.y_scale.to_screen(0)
        h = 40

        path.moveTo(x_vals[0], y0)
        for i in range(len(x_vals)-1):
            x = x_vals[i]
            txt = y_vals[i]
            w = x_vals[i+1] - x_vals[i]
            path.addRect(x, y0-h, w, h)

            path.addText(float(x), float(y0), QtGui.QFont(), str(self.data[1][i]))
        self.path = path
        return path

    def boundingRect(self, *args, **kwargs):
        x = self.data[0]
        y = self.data[1]
        x = self.plot.x_scale.to_screen(x)
        y0 = self.plot.y_scale.to_screen(0)
        if self._bounding_rect is None or True:
            self._bounding_rect = QtCore.QRectF(np.min(x), y0, np.ptp(x), 40)
        return self._bounding_rect

class StyleFactory:
    def __init__(self, colors):
        self.colors = colors
        self.index = 0
        self.pens = {}
        self.brushes = {}
        self.indices = {}

    def get_pen(self, key):
        if key in self.pens:
            return self.pens[key]
        else:
            color = QtGui.QColor(self.colors[(len(self.pens) + 1) % len(self.colors)])
            pen = QtGui.QPen()
            pen.setColor(color)
            pen.setWidthF(1.0)
            self.pens[key] = pen
            return pen

    def get_brush(self, key):
        if key in self.brushes:
            return self.brushes[key]
        else:
            color = QtGui.QColor(self.colors[(len(self.brushes) + 1) % len(self.colors)])
            brush = QtGui.QBrush()
            brush.setColor(color)
            brush.setStyle(Qt.SolidPattern)
            self.brushes[key] = brush
            return brush







