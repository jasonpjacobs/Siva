# -*- coding: utf-8 -*-
"""
This module defines Styles and Stylizer classes.  These classes are used to
define and alter the appearance of objects in the Schematic, based on the
object attributes, view mode, or both.

Copyright 2014, Jason Jacobs
"""
from ..qt_bindings import QtGui, QtCore, Qt


from .color import Color
import numpy as np
import yaml


class ItemStyle(object):
    """ItemStyles define a set of pen and brush settings used to render
    items on the schematic.


    pen_color
    pen_width
    pen_style
    brush_color

    gradient_type
    gradient_color

    shadow
    blur

    anti_alias
    """

    # Maps strings to Qt line style enumerations
    LINE_STYLES = {"solid": Qt.SolidLine,
                   "dash": Qt.DashLine,
                   "dash-dot": Qt.DashDotLine,
                   "dash-dot-dot": Qt.DashDotDotLine,
                   "_": Qt.SolidLine,
                   ".": Qt.DotLine,
                   "-": Qt.DashLine,
                   "-.": Qt.DashDotLine,
                   "-..": Qt.DashDotDotLine
                   }


    _dump_attrs = ['pen_color', 'pen_width','pen_style','brush_color','shadow', 'blur', 'anti_alias',
                   'gradient', 'gradient_color','gradient_type', 'alpha']

    def __init__(self, *args, **kwargs):

        self._pen = None
        self._brush = None
        self.shadow = None
        self.blur = False
        self.gradient = None
        #self.alpha = None

        # Pen color
        if "line_color" in kwargs:
            self.pen_color = kwargs["line_color"]
        elif "line" in kwargs:
            self.pen_color = kwargs["line"]
        elif "pen_color" in kwargs:
            self.pen_color = kwargs["pen_color"]
        elif "color" in kwargs:
            self.pen_color = kwargs["color"]
        else:
            self.pen_color = None

        # Convert to the local Color object
        if self.pen_color is not None:
            self.pen_color = Color(self.pen_color)

        #Pen width
        if "line_width" in kwargs:
            self.pen_width = kwargs["line_width"]
        elif "pen_width" in kwargs:
            self.pen_width = kwargs["pen_width"]
        elif "width" in kwargs:
            self.pen_width = kwargs["width"]
        else:
            self.pen_width = 0

        # Line Style
        self.line_style = None
        if "line_style" in kwargs:
            value = kwargs["line_style"]
            if type(value) == str:
                value = self.LINE_STYLES[value]
            self.line_style = value

        # Brush color
        if "brush_color" in kwargs:
            self.brush_color = kwargs["brush_color"]
        elif "fill_color" in kwargs:
            self.brush_color = kwargs["fill_color"]
        elif "fill" in kwargs:
            self.brush_color = kwargs["fill"]
        elif "color" in kwargs:
            self.brush_color = kwargs["color"]
        else:
            self.brush_color = None

        # Gradient
        self.gradient = False
        self.gradient_color = None
        self.gradient_type = kwargs.get("gradient_type", None)

        if "gradient_type" in kwargs:
            self.gradient_type = kwargs.get("gradient_type")
            assert(self.gradient_type in ("diagonal", "radial", None))
            if self.gradient_type:
                self.gradient = True

        if "gradient_color" in kwargs:
            self.gradient_color = kwargs.get("gradient_color")
            if self.gradient_color:
                self.gradient = True

        # Effects
        if "shadow" in kwargs:
            self.shadow = kwargs["shadow"]

        if "blur" in kwargs:
            self.blur = kwargs["blur"]

        if "glow" in kwargs:
            self.glow = kwargs["glow"]


        # Misc attributes
        if 'anti_alias' in kwargs:
            self.anti_alias = True
        else:
            self.anti_alias = None

        alpha = kwargs.get("alpha", None)
        if alpha is not None:
            alpha = float(alpha)
        self.alpha = alpha

    @property
    def pen(self):
        if self._pen is None or self._dirty:
            # Create the pen
            pen = QtGui.QPen(Color(self.pen_color))
            if self.pen_width is not None:
                pen.setWidthF(self.pen_width)
            if self.line_style is not None:
                pen.setStyle(self.line_style)
            # Add additional transparency
            if self.alpha:
                color = pen.color()
                new_alpha = self.alpha * color.alphaF()
                color.setAlphaF(new_alpha)
                pen.setColor(color)
            self._pen = pen
        return self._pen

    @property
    def brush(self):
        if self._brush is None or self._dirty:
            # Create the brush
            if self.gradient:
                if self.gradient_type == "radial":
                    gradient = QtGui.QRadialGradient(QtCore.QPointF(0,0), 100)
                else:
                    gradient = QtGui.QLinearGradient()

                color1 = Color(self.brush_color)
                if self.gradient_color is not None:
                    color2 = Color(self.gradient_color)
                else:
                    color2 = color1.darker()

                if self.alpha is not None:
                    alpha1 = self.alpha * color1.alphaF()
                    alpha2 = self.alpha * color2.alphaF()
                    color1.setAlphaF(alpha1)
                    color2.setAlphaF(alpha2)

                gradient.setColorAt(0, color1)
                gradient.setColorAt(1.0, color2)
                brush = QtGui.QBrush(gradient)
                brush = gradient
            else:
                color = Color(self.brush_color)
                if self.alpha:
                    alpha = self.alpha * color.alphaF()
                    color.setAlphaF(alpha)
                brush = QtGui.QBrush(color)
            self._brush = brush
        return self._brush


    @brush.setter
    def brush(self, value):
        self._brush = value


    def setup_brush(self, rect):
        brush = self.brush
        # Setup gradient's to work with this item's geometry
        if isinstance(brush, QtGui.QLinearGradient):
            brush.setStart(rect.bottomLeft())
            brush.setFinalStop(rect.topRight())
        elif isinstance(brush, QtGui.QRadialGradient):
            brush.setRadius(max(rect.width(), rect.height()))
        if hasattr(self, 'setBrush'):
            if style.brush is not None and self.fillable:
                self.setBrush(QtGui.QBrush(brush))
        self.brush = brush
        return brush

    def copy(self):
        style_copy = ItemStyle(
                  pen_color=self.pen_color,
                  pen_width=self.pen_width,
                  line_style=self.line_style,
                  brush_color=self.brush_color,
                  anti_alias=self.anti_alias,
                  shadow=self.shadow,
                  blur=self.blur,
                  alpha=self.alpha,
                  gradient=self.gradient,
                  gradient_color=self.gradient_color,
                  gradient_type=self.gradient_type
                  )
        return style_copy

    def __setattr__(self, attr, value):
        object.__setattr__(self, '_dirty', True)
        object.__setattr__(self, attr, value)


    @classmethod
    def yaml_representer(cls, dumper, data):
        tag = u"!Style"
        mapping = {}
        for attr in data.__class__._dump_attrs:
            if hasattr(data, attr):
                value = getattr(data, attr)
                if value:
                    mapping[attr] = value
        return dumper.represent_mapping(tag, mapping)

    @classmethod
    def yaml_constructor(cls, loader, node):
        kwargs = loader.construct_mapping(node)
        return ItemStyle(**kwargs)

yaml.add_representer(ItemStyle, ItemStyle.yaml_representer)
yaml.add_constructor(u"!Style", ItemStyle.yaml_constructor)

class NoStyle(ItemStyle):
    def __init__(self):
        self._pen = None
        self._brush = None
        self.shadow = None
        self.blur = False

        self.pen_color = None
        self.brush_color = None

class Stylizer(object):
    """Adjusts the color, transparency, pen width of an object's appearance"""

    def __init__(self):
        self.enabled = True

    def apply(self, style, obj):
        return style


class AlphaByPos(Stylizer):
    """A stylizer that adjust the transparency of an object
    based on its position
    """
    def brush(self, brush, obj):
        length = np.sqrt(obj.pos()[0] ** 2 + obj.pos()[1] ** 2)
        alpha = max(0.01, length / 400)
        alpha = min(alpha, 1.0)
        color = brush.color()
        color.setAlphaF(alpha)
        brush.setColor(color)
        return brush

    def pen(self, pen, obj):
        pen.setWidthF(0.25)
        pen.setColor(Qt.black)
        return pen


class ColorHighlighter(Stylizer):
    """ A stylizer that changes the color (excluding transparency)
    to Items with item.highlighted == True
    """
    def __init__(self, color=Qt.yellow):
        Stylizer.__init__(self)
        self.color = color

    def apply(self, style, obj):
        if obj.highlighted:
            style.brush_color = self.color
            style.pen_color = self.color
        return style


class BoldStylizer(Stylizer):
    def __init__(self, width=1.5):
        self.width_ratio = width

    def apply(self, style, obj):
        style.pen_width = style.pen_width * self.width_ratio
        return style


