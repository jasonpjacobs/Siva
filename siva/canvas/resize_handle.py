# -*- coding: utf-8 -*-
"""
Defines Control Points used to change the size and rotation of Canvas Items
"""

from ..qt_bindings import QtGui, QtCore, Qt


#from .canvas import items
from .color import Color

from functools import partial
import math
import pdb

class ResizeHandle(QtGui.QGraphicsItem):
    def __init__(self, pos, parent=None, size=10, z=1, callback=None, style=None, cursor=Qt.SizeAllCursor, moveable=False):
        QtGui.QGraphicsItem.__init__(self, parent=parent, style=style)

        #self.item = item
        self.parent = parent
        self.callback = callback
        self.style = style
        self.setZValue(z)

        self.size = size

        # So the items stays the same size in the view
        self.setFlag(QtGui.QGraphicsItem.ItemIgnoresTransformations)

        self.setCursor(cursor)
        self.setPos(pos)
        self.setActive(True)

        self.moveable = moveable

    #def setPos(self, value):
    #    return canvas.items.Item.setPos(self, value)

    def setup_painter(self, painter):
        if self.style is not None:
            pen = self.style.pen
            brush = self.style.setup_brush(self.boundingRect())
        else:
            pen = QtGui.QPen(Qt.black)
            pen.setWidth(1)
            brush = QtGui.QBrush(Color('#5965A8'))

        painter.setPen(pen)
        painter.setBrush(brush)

class SquareHandle(ResizeHandle):
    def boundingRect(self, *args, **kwargs):
        s=self.size
        return QtCore.QRectF(-s/2, -s/2, s, s)

    def paint(self, painter, option, widget):
        d=self.size
        rect = QtCore.QRectF(-d/2, -d/2, d, d)

        self.setup_painter(painter)
        painter.drawRect(rect)

class CircleHandle(ResizeHandle):
    def boundingRect(self, *args, **kwargs):
        s=self.size
        return QtCore.QRectF(-s/2, -s/2, s, s)

    def paint(self, painter, option, widget):
        d=self.size
        self.setup_painter(painter)
        painter.drawEllipse(-d/2, -d/2, d, d)

class ResizeRect(QtGui.QGraphicsItemGroup):

    def __init__(self, item, size=10, style=None):
        QtGui.QGraphicsItemGroup.__init__(self, parent=None, style=None)
        self.__rotation = 0

        #self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges , True)
        self.item = item
        self.size = size
        self.rect = QtCore.QRectF(item.mapToScene(item.boundingRect().topLeft()),
                                  item.mapToScene(item.boundingRect().bottomRight()))
        self.style = style
        rect = self.rect

        z=item.zValue() + 1
        self.setZValue(z)


        z = z + 1

        x1, y1, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        x2, y2 = x1 + w, y1 + h
        xm, ym = (x1 + w/2), y1 + h/2

        # Top Right
        self.tr = SquareHandle(QtCore.QPointF(x2, y2), size=size, parent=self, z=z,
                                callback=partial(self.modify_sides, sides='tr'),
                                cursor=Qt.SizeBDiagCursor,
                                style=self.style
                                )

        # Top left
        self.tl = SquareHandle(QtCore.QPointF(x1, y2), size=size, parent=self, z=z,
                                callback=partial(self.modify_sides, sides='tl'),
                                cursor=Qt.SizeFDiagCursor,
                                style=self.style
                                )
        # Bottom right
        self.br = SquareHandle(QtCore.QPointF(x2, y1), size=size, parent=self, z=z,
                                callback=partial(self.modify_sides, sides='br'),
                                cursor=Qt.SizeFDiagCursor,
                                style=self.style
                                )
        # Bottom left
        self.bl = SquareHandle(QtCore.QPointF(x1, y1), size=size, parent=self, z=z,
                                callback=partial(self.modify_sides, sides='bl'),
                                cursor=Qt.SizeBDiagCursor,
                                style=self.style
                                )

        self.mr = SquareHandle(QtCore.QPointF(x2, ym), size=size-2, parent=self, z=z,
                                callback=partial(self.modify_sides, sides='r'),
                                cursor=Qt.SizeHorCursor,
                                style=self.style
        )

        self.ml = SquareHandle(QtCore.QPointF(x1, ym), size=size-2, parent=self, z=z,
                                callback=partial(self.modify_sides, sides='l'),
                                cursor=Qt.SizeHorCursor,
                                style=self.style
        )

        self.top = SquareHandle(QtCore.QPointF(xm, y2), size=size-2, parent=self, z=z,
                                callback=partial(self.modify_sides, sides='t'),
                                cursor=Qt.SizeVerCursor,
                                style=self.style
                                )

        self.bottom = SquareHandle(QtCore.QPointF(xm, y1), size=size-2, parent=self, z=z,
                                callback=partial(self.modify_sides, sides='b'),
                                cursor=Qt.SizeVerCursor,
                                style=self.style
                                )

        self.rot = CircleHandle(QtCore.QPointF(xm, y2+20), size=size-2, parent=self, z=z,
                                callback=self.modify_rotation,
                                cursor=Qt.SizeVerCursor,
                                style=self.style,
                                moveable=False
                                )

        self.addToGroup(self.tr)
        self.addToGroup(self.tl)
        self.addToGroup(self.br)
        self.addToGroup(self.bl)
        self.addToGroup(self.mr)
        self.addToGroup(self.ml)
        self.addToGroup(self.top)
        self.addToGroup(self.bottom)
        self.addToGroup(self.rot)

        pdb.set_trace()
        #self.rotate(item.rotation)

    def paint(self, painter, options, widget):
        QtGui.QGraphicsItemGroup.paint(self, painter, options, widget)
        pen = QtGui.QPen(Qt.blue)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.drawRect(self.rect)

    def modify_sides(self, pos, sides,coords):
        """
        Updates the geometry of the ResizeRect using
        the new position of one of its control points.

        :param pos: Position of the moved control point
        :param sides: Side(s) of the ResizeRect to adjust
        :return: None
        """


        x,y = pos.x(), pos.y()
        side = sides

        # The "top" and "bottom*' methods assume the default
        # Qt coordinate system, where the values increase downwards.
        # Therefore, we need to get this boundingRects topLeft corner
        # for our bottomLeft
        bl = self.rect.topLeft()
        x1, y1 = bl.x(), bl.y()

        tr = self.rect.bottomRight()
        x2, y2 = tr.x(), tr.y()

        if side == "t":
            y2=y

        elif side == "b":
            y1 = y

        elif side == "l":
            x1 = x

        elif side == "r":
            x2 = x

        elif side == "tr":
            x2 = x
            y2 = y

        elif side == "tl":
            x1 = x
            y2 = y

        elif side == "bl":
            x1 = x
            y1 = y

        elif side == "br":
            x2 = x
            y1 = y

        # Have the lowerleft and upper right coords been swapped?
        if (x2, x1):
            pass
        if y2 < y1:
            pass

        # Again, need to flip upside-down
        self.rect.setTopLeft(QtCore.QPointF(x1, y1))
        #self.setPos(QtCore.QPointF(x1, y1))
        self.rect.setBottomRight(QtCore.QPointF(x2, y2))

        self.place_control_points()
        self.item.resize(self)

    def place_control_points(self):
        """
        Places control points at the corners and in the middle of the
        sides of the ResizeRect.

        :return: None
        """
        rect = self.rect
        x1, y1, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        x2, y2 = x1 + w, y1 + h
        xm, ym = (x1 + w/2), y1 + h/2

        self.tl.setPos(QtCore.QPointF(x1,y2))
        self.top.setPos(QtCore.QPointF(xm, y2))
        self.tr.setPos(QtCore.QPointF(x2,y2))

        self.ml.setPos(QtCore.QPointF(x1, ym))
        self.mr.setPos(QtCore.QPointF(x2, ym,))

        self.bl.setPos(QtCore.QPointF(x1,y1))
        self.bottom.setPos(QtCore.QPointF(xm,y1))
        self.br.setPos(QtCore.QPointF(x2,y1))

        self.rot.setPos(QtCore.QPointF(xm, y2+20))


    def modify_rotation(self, pos, coords):
        delta = pos - self.center()
        line = QtCore.QLineF(self.center(), coords)
        #angle = (90 - line.angle() ) % (360)
        delta_angle = (90 + line.angle()) % 360

        # Snap angle
        delta_angle = delta_angle - (delta_angle % 5)
        angle = self.rotation() + delta_angle
        center = self.center()

        # Rotate ourselves
        self.rotate(angle)

        # And our item
        self.item.rotate(delta_angle)

    @property
    def width(self):
        return self.rect.width()

    @property
    def height(self):
        return self.rect.height()

    @property
    def origin(self):
        return self.rect.center()

    def center(self):
        return self.rect.center()

    def rotate(self, angle):
        center = self.center()
        self.__rotation = angle % 360
        self.setTransform(
            QtGui.QTransform().translate(center.x(), center.y()).rotate(-1*angle).translate(-1*center.x(), -1*center.y())
        )

    def rotation(self):
        return self.__rotation
