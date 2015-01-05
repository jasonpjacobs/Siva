# -*- coding: utf-8 -*-
"""
Defines the graphical primitives drawn onto the schematic.
"""
from ..qt_bindings import QtGui, QtCore, Qt


from .styles import ItemStyle
from .color import Color

import numbers
import yaml
import pdb
import inspect
from collections import OrderedDict

# ----------------------------------------------------------------
#    Item Class
# ----------------------------------------------------------------
#class Item(QtGui.QGraphicsObject):
class Item:

    """Base class for all objects rendered on the schematic.

    These classes extend the QGraphicsItem classes with hooks
    to dynamically render the items, based on modes or attributes.

    The appearance of an item on the canvas is determined by a Style object.
    Style objects contain settings for line and fill colors, line width,
    alpha value (transparency). and effects such as blur, drop shadow,
    and colorization.

    Dynamic rendering takes place through three processes.  When an item
    is getting painted, its *style* attribute is used to setup the pen
    and brush.  This *style* attribute is a property that can refer to
    an instance of a *Style* class, or be reimplemented in subclasses
    to produce pen/brush colors, widths, and effects that depend on
    an objects attributes.

    The style is then altered based on several Item properties:
    * bold
    * alpha
    * colorize
    * shadow
    * blur

    Finally, the item's style is passed through *Stylizer* objects that
    can alter the properties of the style.
    """

    # Default outline style, used if the Canvas does not
    # insert an explicit style in the the Item's style map.
    _default_outline_style = ItemStyle(pen_color=Color(0, 0, 128, 128),
                                      line_width=2,
                                    )

    # Default highlight style - Colors item yellow
    _default_highlight_style = ItemStyle(fill_color=Color(255, 0, 255,))

    _default_handle_style = ItemStyle(line_color='black',
                                      fill_color='white',
                                      gradient_color=Color('darkBlue',),
                                      gradient_type='radial'
    )


    _dump_attrs = ['style', 'origin']
    _dump_tag = 'Item'

    outline_width = 10

    @classmethod
    def yaml_representer(cls, dumper, data):
        tag = u"!{}".format(data.__class__._dump_tag)
        mapping = OrderedDict()
        for attr in data.__class__._dump_attrs:
            value = getattr(data, attr)
            mapping[attr] = value
        return dumper.represent_mapping(tag, mapping)

    @classmethod
    def yaml_constructor(cls, loader, node):
        val=loader.construct_mapping(node, deep=True)
        return cls(**val)

    def __init__(self, style=None, style_map=None, *args, **kwargs):
        #QtCore.QObject.__init__(self)
        self.name = kwargs.get("name", None)

        # Property initialization
        self._bold = False
        self.__selected = False
        self.__highlight = False
        self.__colorized = False
        self.__outline = False

        # Flags
        self.__selectable = True
        self.__movable = False
        self.anti_alias = True
        self.fillable = True  # Shapes are fillable, lines, text are not.

        # Define the normal style of the item
        if style is None:
            self.style = ItemStyle(**kwargs)
        else:
            self.style = style

        # The Canvas can add mode specific styles via this dict
        if style_map is None:
            self.style_map = {}

        # Fixed QGraphicsItem flags
        #self.setAcceptHoverEvents(True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, self.__movable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, self.__selectable)
        self.modes = []

        self.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)

        self.style_cache_valid = False

        # Used to adjust the bounding rect when
        # custom effects are applied
        self._bounding_rect_pad = 0

        self._bounding_rect = None

    def boundingRect(self):
        print("Item Bonding rect called", self)
        if self._bounding_rect is None:
            dx=self._bounding_rect_pad
            print("Creating bounding rect for [], pad={}".format(self, dx))
            self._bounding_rect = self.bounds.adjusted(-dx, -dx, dx, dx)

        return self._bounding_rect

    # ----------------------------------------------------------------
    #    Custom rendering
    # ----------------------------------------------------------------
    def setupForPaint(self, painter, modes=("normal", "highlight", "selection",
                                             "bold")):
        if self.style._dirty is False:
            style = self.style_cache
            print("Caching style")
        else:
            # Start with the default style
            style = self.style.copy()

            # Keep a reference to the current style
            # to prevent garbage collection
            #self.current_style = style

            # If the item is highlighted, apply the Canvas' "highlight" stylizer
            canvas = self.scene()
            if self.highlight:
                stylizer = canvas.style_map["highlight"]
                if stylizer is not None:
                    style = stylizer.apply(style, obj=self)

            # Give each tool's stylizer a chance to modify the style
            for tool in canvas.active_tools:
                stylizer = tool.get_style()
                if stylizer is not None:
                    style = stylizer.apply(style, obj=self)

            self.style_cache = style
            #self.style_cache_valid = True

        # Item modifications
        # (To do...)

        # Setup the pen/brush
        if hasattr(self, 'setPen') and style.pen is not None:
            self.setPen(QtGui.QPen(style.pen))

        brush = style.setup_brush(rect=self.boundingRect())
        if hasattr(self, 'setBrush'):
            if style.brush is not None and self.fillable:
                self.setBrush(QtGui.QBrush(brush))

        painter.setPen(style.pen)
        painter.setBrush(brush)

        # Create a new shadow effect if the requested
        # shadow is different from the current one
        # The shadow and blur attributes will
        # cache the result
        if style.shadow and style.shadow != self.shadow:
            self.shadow = style.shadow
        if style.blur and style.blur != self.blur:
            self.blur = style.blur

        if style.anti_alias or self.anti_alias:
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

    def paint(self, painter, option, widget):
        if hasattr(self, 'draw_outline') and self.outline:
            self.draw_outline(painter, None)
        self.setupForPaint(painter, self.modes)
        self.draw_item(painter, option, widget)

    def draw_outline(self, painter, style=None, width=10):
        """Draws an outline around the given shape,
        using the *outline* Style
        """
        style = self.style_map.get("outline", Item._default_outline_style)
        pen = style.pen

        stroker = QtGui.QPainterPathStroker()
        stroker.setWidth(width - style.pen_width )
        #self._bounding_rect_pad = width
        self._bounding_rect = None  # Force recalculation

        path = self.shape()
        new_path = (stroker.createStroke(path) + path).simplified()

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.strokePath(new_path, pen)

    def edit(self):
        from .resize_handle import ResizeRect
        self.resizer = ResizeRect(item=self, style=self._default_handle_style)
        scene = self.scene()
        if scene is not None:
            self.scene().add(self.resizer)


    def resize(self, control):
        raise(NotImplementedError)

    @property
    def origin(self):
        return [self.pos().x(), self.pos().y()]

    @origin.setter
    def origin(self, value):
        self.x = value.x()
        self.y = value.y()
        self.setPos(value)

    def rotate(self, angle):
        # To force clockwise rotation
        QtGui.QGraphicsItem.rotate(self, -1*angle)

    @property
    def rotation(self):
        return self.__rotation

    @rotation.setter
    def rotation(self, value):
        value = value % 360
        self.__rotation = value
        self.rotate(value)

    # ----------------------------------------------------------------
    # Style properties.  Default implementation just returns
    # the style created during initialization.  Subclasses can
    # return attribute dependent styles.
    # ----------------------------------------------------------------
    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        self._style = value

    @style.deleter
    def style(self):
        del(self._style)

    # ----------------------------------------------------------------
    #    Editing API
    # ----------------------------------------------------------------
    def flip(self, x=False, y=False):
        x = -1. if x else 1.
        y = -1. if y else 1.
        t = self.transform()
        t=t.scale(x,y)
        self.setTransform(t)

    # ----------------------------------------------------------------
    #    Event handling - Used in interactive mode only.
    # ----------------------------------------------------------------
    def hoverEnterEvent(self, event):
        event.ignore()

    def hoverLeaveEvent(self, event):
        event.ignore()

    def mousePressEvent(self, event):
        print("Item mouse press")
        event.ignore()

    def mouseMoveEvent(self, event):
        print("Item mouse move")
        event.ignore()

    def mouseReleaseEvent(self, event):
        print("Item Mouse release")
        event.ignore()

    def __repr__(self):
        return "{}(name='{}')".format(str(self.__class__), self.name)

    # ----------------------------------------
    #  Property getters/setters
    # ----------------------------------------
    def getBold(self):
        return self.__bold

    def getSelected(self):
        return self.__selected

    def getAlpha(self):
        return self.style.alpha

    def getGlow(self):
        return self.__glow

    def getOutline(self):
        return self.__outline

    def getHighlight(self):
        return self.__highlight

    def getColorized(self):
        return self.__colorized

    def getShadow(self):
        return self.__shadow

    def getBlur(self):
        return self.__blur

    def getSelectable(self):
        return self.__selectable

    def getMovable(self):
        return self.__movable

    def setBold(self, value):
        if value is not False or value is not None:
            self.__bold = True
        else:
            self.__bold = False
        # The value can also be a ratio
        if isinstance(value, numbers.Number):
            self.__bold_ratio = value
        else:
            self.__bold_ratio = 1.5  # default

    def setSelected(self, value):
        self.__selected = value
        self.update()

    def setAlpha(self, value):
        self.style.alpha = value
        self.update()

    def setGlow(self, value):
        self.__glow = value
        self.update()

    def setOutline(self, value):
        self.__outline = value

        if value:
            style = self.style_map.get("outline", Item._default_outline_style)
            self._bounding_rect_pad = self.outline_width
        else:
            self._bounding_rect_pad = 0
        # Force bounding box recalculation
        self._bounding_rect = None
        self.update()

    def setHighlight(self, value):
        self.__highlight = value
        self.update()

    def setColorized(self, value):
        self.__colorized = QtGui.QColor(value)
        self.update()

    def setShadow(self, value):
        if not hasattr(self, '_shadow_value'):
            self._shadow_value = None
        # Caching
        if value == self._shadow_value:
            return

        if isinstance(self.graphicsEffect(),
                          QtGui.QGraphicsDropShadowEffect):
                self.setGraphicsEffect(None)

        if value is not False and value is not None:
            self.__shadow = True

            # Store the value given.  If an item style requests
            # the same shadow type, we don't need to recreate
            # the graphics effect object
            self._shadow_value = value

            # Create a new effect
            self._shadow_effect = QtGui.QGraphicsDropShadowEffect()
            self._shadow_effect.setBlurRadius(5)
            self._shadow_effect.setOffset(2)


            # Colorize
            if value is not True:
                self.__shadow_color = QtGui.QColor(value)
                self._shadow_effect.setColor(QtGui.QColor(self.__shadow_color))
            self.setGraphicsEffect(self._shadow_effect)
        else:
            self.__shadow = False
            self._shadow_value = None
        self.update()

    def setBlur(self, value):
        if not hasattr(self, '_blur_value'):
            self._blur_value = value
        # Caching
        elif value == self._blur_value:
            return

        if isinstance(self.graphicsEffect(),
                          QtGui.QGraphicsBlurEffect):
                self.setGraphicsEffect(None)

        self._blur_value = value
        if value is not False and value is not None:
            self.__blur = True

            # Store the value given.  If an item style requests
            # the same value, we don't need to recreate
            # the effect

            # Create a new effect
            self.__blur_effect = QtGui.QGraphicsBlurEffect()

            # Custom blur radius
            if value is not True:
                self.__blur_radius = float(value)
                self.__blur_effect.setBlurRadius(self.__blur_radius)
            self.setGraphicsEffect(self.__blur_effect)
        else:
            self.__blur = False
        self.update()

    def setSelectable(self, value):
        self.__selectable = value

    def setMovable(self, value):
        self.__movable = value

    # Property definitions
    bold = property(getBold, setBold, None, "bold")
    selected = property(getSelected, setSelected, None, "selected")
    alpha = property(getAlpha, setAlpha, None, "alpha")
    highlight = property(getHighlight, setHighlight, None, "highlight")
    highlighted = property(getHighlight, None, None, "highlighted")
    colorized = property(getColorized, setColorized, None, "colorized")
    shadow = property(getShadow, setShadow, None, "shadow")
    outline = property(getOutline, setOutline, None, 'outline')
    blur = property(getBlur, setBlur, None, "blur")
    selectable = property(getSelectable, setSelectable, None, "selectable")
    movable = property(getMovable, setMovable, None, "movable")

yaml.add_representer(Item, Item.yaml_representer)
yaml.add_constructor(u'!Item', Item.yaml_constructor)




class Rect(Item, QtGui.QGraphicsRectItem):
    """A rectangle object, defined by its position (x,y), width and height"""

    # Attributes for serialization
    _dump_attrs = ('origin', 'width', 'height', 'style', 'name', 'radius')
    _dump_tag = 'Rect'

    def __init__(self, x=None, y=None, width=100, height=100, origin=None, radius=10, *args, **kwargs):
        QtGui.QGraphicsRectItem.__init__(self, -width/2, -height/2, width/2, height/2)
        Item.__init__(self, **kwargs)

        assert self._bounding_rect is None

        if origin is None and x is not None and y is not None:
            self.x = x
            self.y = y
            self.origin = QtCore.QPointF(x * 1.0, y * 1.0)
        elif origin is not None and len(origin) == 2:
            self.x = origin[0]
            self.y = origin[1]
            self.origin = QtCore.QPointF(self.x * 1.0, self.y * 1.0)
        else:
            raise ValueError("Rect create with incorrect arguments: {}".format([x,y,origin]))

        self.width = width
        self.height = height
        self.radius = radius
        self.bounds = QtCore.QRect(-width/2, -height/2, width, height)
        self.setTransformOriginPoint(QtCore.QPointF(self.origin[0], self.origin[1]))

    def resize(self, control):
        self.prepareGeometryChange()
        self.setRect(control)

    def setRect(self, rect):
        self.width = rect.width
        self.height = rect.height
        self.origin = rect.center()
        self.bounds = QtCore.QRect(-self.width/2, -self.height/2, self.width, self.height)

    def paint(self, painter, option, widget):
        Item.paint(self, painter, option, widget)

    def draw_item(self, painter, *args):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        w = self.width
        h = self.height
        painter.drawRoundedRect(-w/2, -h/2, w, h, self.radius,
                                self.radius, Qt.AbsoluteSize)

    def boundingRect(self):
        if self._bounding_rect is None:
            if self.outline:
                dx = self.outline_width
            else:
                dx=self.style.pen_width
            self._bounding_rect = QtCore.QRectF(self.bounds.adjusted(-dx, -dx, dx, dx))

        return self._bounding_rect

yaml.add_representer(Rect, Rect.yaml_representer)
yaml.add_constructor(u'!Rect', Rect.yaml_constructor)

class Line(QtGui.QGraphicsLineItem, Item):
    """ A line, defined by its start and end points
     or by the coords x1,y1 and x2,y2
    """
    _dump_attrs = ('start','end', 'style')
    _dump_tag = 'Line'

    def __init__(self, x1=None, y1=None, x2=None, y2=None, start=None, end=None, **kwargs):

        # Temporary settings.  These will get overwritten as the other
        # attributes are set when the init args are parsed
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0

        if x1 is not None and y1 is not None and x2 is not None and y2 is not None:
            start = QtCore.QPointF(x1, y1)
            end = QtCore.QPointF(x2, y2)
        elif x1 and y1 and not start and not end:
            # Two points were provided as args (not keywords)
            start, end = QtCore.QPointF(x1[0], x1[1]), QtCore.QPointF(y1[0], y1[1])
        elif start and end:
            start, end = QtCore.QPointF(start[0], start[1]), QtCore.QPointF(end[0], end[1])
        else:
            pdb.set_trace()
            raise ValueError("Incorrect arguments for Line type: {}".format((x1, y1, x2, y2, start, end)))

        QtGui.QGraphicsLineItem.__init__(self, 0, 0, end.x()-start.x(), end.y()-start.y())

        # Capture the styles
        Item.__init__(self, **kwargs)

        self.origin = start
        self.start = start
        self.end = end
        self.fillable = False

    @property
    def start(self):
        return [self.x1, self.y1]

    @start.setter
    def start(self, value):
        self.x1 = value.x()
        self.y1 = value.y()
        self.setPos(value)
        self.setLine(0, 0, self.x2-self.x1, self.y2 - self.y1)

    @property
    def end(self):
        return [self.x2, self.y2]

    @end.setter
    def end(self, value):
        self.x2 = value.x()
        self.y2 = value.y()
        self.setLine(0, 0, self.x2-self.x1, self.y2 - self.y1)

    def paint(self, painter, option, widget):
        Item.paint(self, painter, option, widget)

    def draw_item(self, painter, option, widget, *args):
        QtGui.QGraphicsLineItem.paint(self, painter, option, widget)
        pass

    def boundingRect(self):
        if self._bounding_rect is None:
            rect = QtGui.QGraphicsLineItem.boundingRect(self)
            if self.outline:
                w = self.outline_width
            else:
                w = self.style.pen_width
            self._bounding_rect = rect.adjusted(-1*w, -1*w, w, w)
        return self._bounding_rect

yaml.add_representer(Line, Line.yaml_representer)
yaml.add_constructor(u'!Line', Line.yaml_constructor)

class Circle(QtGui.QGraphicsEllipseItem, Item):
    def __init__(self, x=None, y=None, r=1, origin=None, *args, **kwargs):

        self.radius = float(r)

        QtGui.QGraphicsEllipseItem.__init__(self, -r/2, -r/2, r, r)
        Item.__init__(self, **kwargs)
        if origin:
            if len(origin) == 2:
                self.origin = QtCore.QPointF(origin[0], origin[1])
            else:
                raise(ValueError, "Incorrect argument type for origin: {}".format(origin))
        elif x is not None and y is not None:
            self.origin = QtCore.QPointF(x * 1.0, y * 1.0)
        else:
            raise
        self.setPos(self.origin[0], self.origin[1])

    # Attributes for serialization
    _dump_attrs = ['style', 'origin', 'radius']
    _dump_tag = 'Circle'

    def paint(self, painter, option, widget):
        Item.paint(self, painter, option, widget)

    def draw_item(self, painter, option, *args):
        QtGui.QGraphicsEllipseItem.paint(self, painter, option)

    def boundingRect(self):
        if self._bounding_rect is None:
            rect = QtGui.QGraphicsEllipseItem.boundingRect(self)
            if self.outline:
                w = w = self.outline_width
            else:
                w = self.style.pen_width
            self._bounding_rect = rect.adjusted(-1*w, -1*w, w, w)
        return self._bounding_rect

yaml.add_representer(Circle, Circle.yaml_representer)
yaml.add_constructor(u'!Circle', Circle.yaml_constructor)

class Ellipse(QtGui.QGraphicsEllipseItem, Item):

    # Attributes for serialization
    _dump_attrs = ('origin', 'width', 'height','style')
    _dump_tag = 'Ellipse'

    def __init__(self, x=None, y=None, width=1, height=1, origin=None, *args, **kwargs):

        QtGui.QGraphicsEllipseItem.__init__(self, -width/2, -height/2, width, height)
        Item.__init__(self, **kwargs)

        if origin:
            if len(origin) == 2:
                self.origin = QtCore.QPointF(origin[0], origin[1])
            else:
                raise(ValueError, "Incorrect argument type for origin: {}".format(origin))
        elif x is not None and y is not None:
            self.origin = QtCore.QPointF(x * 1.0, y * 1.0)
        else:
            raise

        self.setPos(self.origin[0], self.origin[1])
        self.width = width
        self.height = height
        self.bounds = QtCore.QRect(-width/2, -height/2, width, height)

    def paint(self, painter, option, widget):
        Item.paint(self, painter, option, widget)

    def draw_item(self, painter, option, *args):
        QtGui.QGraphicsEllipseItem.paint(self, painter, option)

    def boundingRect(self):
        if self._bounding_rect is None:
            rect = QtGui.QGraphicsEllipseItem.boundingRect(self)
            if self.outline:
                w = w = self.outline_width
            else:
                w = self.style.pen_width
            self._bounding_rect = rect.adjusted(-1*w, -1*w, w, w)
        return self._bounding_rect


yaml.add_representer(Ellipse, Ellipse.yaml_representer)
yaml.add_constructor(u'!Ellipse', Ellipse.yaml_constructor)

class Polygon(QtGui.QGraphicsPolygonItem, Item):
    def __init__(self, points, polygon=None, **kwargs):
        if points is not None:
            points = [QtCore.QPointF(p[0], p[1]) for p in points]
            poly = QtGui.QPolygonF(points)
        elif polygon is not None:
            poly = polygon

        QtGui.QGraphicsPolygonItem.__init__(self, poly)
        Item.__init__(self, **kwargs)

    def paint(self, painter, option, widget):
        Item.paint(self, painter, option, widget)
        
    def draw_item(self, painter, option, widget):
        QtGui.QGraphicsPolygonItem.paint(self, painter, option, widget)

    def boundingRect(self):
        if self._bounding_rect is None:
            rect = QtGui.QGraphicsPolygonItem.boundingRect(self)
            if self.outline:
                w = self.outline_width
            else:
                w = self.style.pen_width
            self._bounding_rect = rect.adjusted(-1*w, -1*w, w, w)
        return self._bounding_rect

class Polyline(QtGui.QGraphicsItem, Item):
    def __init__(self, points=None, polygon=None, **kwargs):

        QtGui.QGraphicsItem.__init__(self)
        Item.__init__(self, **kwargs)
        if points is not None:
            if not isinstance(points[0], QtCore.QPointF):
                self.points = [QtCore.QPointF(p[0], p[1]) for p in points]
            else:
                self.points = list(points)
        else:
            self.points = []
        #     #self.polygon = QtGui.QPolygonF(points)
        # elif polygon:
        #     self.polygon = polygon
        # else:
        #     self.polygon = None

        # Call superclass constructor
        #QtGui.QGraphicsPolygonItem.__init__(self, self.polygon)

    _dump_attrs = ['origin', 'style', 'points']
    _dump_tag = 'Polyline'


    def paint(self, painter, option, widget):
        Item.paint(self, painter, option, widget)
        
    def draw_item(self, painter, option, widget):
        painter.drawPolyline(*self.points)

    def add_point(self, point):
        point = QtCore.QPointF(point)
        self.prepareGeometryChange()
        self.points.append(point)
        self._compute_bounding_box()

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, value):
        self.prepareGeometryChange()
        self._points = value
        self._compute_bounding_box()

    def _compute_bounding_box(self):
        # Compute the bounding rect
        if self._points:
            x_vals = [p.x() for p in self._points]
            y_vals = [p.y() for p in self._points]
            self._bounding_rect = QtCore.QRect(min(x_vals), min(y_vals),
                                    max(x_vals)-min(x_vals), max(y_vals)-min(y_vals))
        else:
            self._bounding_rect = QtCore.QRectF()

    def draw_outline(self, painter, style=None, width=10):
        painter.drawPath(self.shape())

    def boundingRect(self, *args, **kwargs):
        if self._bounding_rect is None:
            self._compute_bounding_box()
            if self.outline:
                dx = self.outline_width
            else:
                dx = self.style.pen_width
            rect = self._bounding_rect.adjusted(-dx, -dx, dx, dx)
            self._bounding_rect = rect
        return QtCore.QRectF(self._bounding_rect)

    def shape(self):
        path = QtGui.QPainterPath()
        path.moveTo(self.points[0])
        points = self.points
        for point in points[1:]:
            path.lineTo(point)
        return path

yaml.add_representer(Polyline, Polyline.yaml_representer)
yaml.add_constructor(u'!Polyline', Polyline.yaml_constructor)

# ---------------------------------------------------------------
#   YAML constructor/representer for the QPointF class
# ---------------------------------------------------------------
def qpoint_representer(dumper, data):
        tag = u"!Point"
        return dumper.represent_sequence(tag, [data.x(), data.y()])

def qpoint_constructor(loader, node):
    val=loader.construct_sequence(node, deep=True)
    return QtCore.QPointF(val[0], val[1])

yaml.add_representer(QtCore.QPointF, qpoint_representer)
yaml.add_constructor(u"!Point", qpoint_constructor)

class Text(QtGui.QGraphicsTextItem, Item):
    def __init__(self, txt, x=0, y=0, bold=False, italic=False,
                 underline=False, overline=False, size=None, width=-1, height=None,
                 **kwargs):
        if "anti_alias" not in kwargs:
            kwargs["anti_alias_text"] = True

        QtGui.QGraphicsTextItem.__init__(self, txt)
        Item.__init__(self, kwargs)

        font = self.font()

        if size:
            font.setPointSize(size)

        font.setItalic(italic)
        font.setBold(bold)
        font.setUnderline(underline)
        font.setOverline(overline)
        self.setFont(font)

        self.setPos(x, y)
        self.scale(1, -1)

        self.setTextInteractionFlags(Qt.TextEditorInteraction)

        fm = QtGui.QFontMetricsF(font)
        if width is not None:
            self.width = width
        else:
            self.width = fm.width(txt)

        if height is not None:
            self.height = height
        else:
            self.height = fm.height()

    def paint(self, painter, option, widget):
        self.draw_item(painter, option, widget)
        
    def draw_item(self, painter, options, widget):
        QtGui.QGraphicsTextItem.paint(self, painter, options, widget)

    def boundingRect(self, *args, **kwargs):
        if self._bounding_rect is None:
            w = self.document().size().width()
            h = self.document().size().height()
            self._bounding_rect = QtCore.QRectF(0, 0, w, h)
        return self._bounding_rect



class Group(QtGui.QGraphicsItemGroup, Item):
    """
    """
    
    # Setting the following attributes will also
    # set he corresponding attributes in the
    # Group's children.
    CHILD_ATTRITBUTES = ('alpha', 'glow', 'outline',
        'highlight', 'colorized', 'shadow')

    _dump_attrs = ["origin", "style", "items"]
    _dump_tag = "Group"

    def __init__(self, items = None, x=0, y=0, origin=None, *args, **kwargs):

        QtGui.QGraphicsItemGroup.__init__(self)
        Item.__init__(self, **kwargs)
        self.__items = []
        if items:
            self.items = items
        else:
            self.items = []

        if x and y:
            self.x=x
            self.y=y
            self.origin= QtCore.QPointF(self.x, self.y)
        elif origin:
            self.origin= QtCore.QPointF(origin[0], origin[1])


    def add(self, item):
        self.__items.append(item)
        item.setParentItem(self)
        self.addToGroup(item)

    def paint(self, painter, option, widget):
        Item.paint(self, painter, option, widget)

    def draw_item(self, painter, option, widget):
        return None

    def draw_outline(self, *args, **kwargs):
        pass

    def __setattr__(self, attr, value):
        if attr in Group.CHILD_ATTRITBUTES:
            for child in self.childItems():
                setattr(child, attr, value)
        object.__setattr__(self, attr, value)

    @property
    def items(self):
        return self.childItems()

    @items.setter
    def items(self, items):
        for item in items:
            self.add(item)

yaml.add_representer(Group, Group.yaml_representer)
yaml.add_constructor(u"!Group", Group.yaml_constructor)