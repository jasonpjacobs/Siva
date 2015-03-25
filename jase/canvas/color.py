"""
Created on Jun 2, 2014

@author: Jase
"""

from ..qt_bindings import QtGui, QtCore, Qt
import yaml
import pdb


class Color(QtGui.QColor):
    qt_color_names = QtGui.QColor.colorNames()

    color_shortcuts = {
        'r' : (255, 0, 0),
        'g' : (0, 0, 255),
        'b' : (0, 255, 0),
        'y' : (255, 255, 0),
        'm' : (255, 0, 255),
        'c' : (0, 255, 255),
        'w' : (255, 255, 255),
        'k' : (0, 0, 0)
    }
    def __init__(self, *args, alpha=None):

        # If a Qt color enum is given, just initialize the parent class
        # otherwise, covert to an integer RGB or RGBA format.
        if len(args) == 1:
            val = args[0]
            # Check for None (tranparent)
            if val is None:
                self._args = None
                return QtGui.QColor.__init__(self, QtCore.Qt.transparent)

            elif type(val) is str:
                # Qt or Unix Color name
                if val.lower() in Color.qt_color_names:
                    self._args = val
                    return QtGui.QColor.__init__(self, val)
                # Matplotlib color name
                if val in Color.color_shortcuts:
                    vals = Color.color_shortcuts[val]
                    self._args = vals
                # Hex RGB
                elif val[0] == "#" and len(val) == 7:
                    # Hex coding
                    self._args = val
                    vals = [int(v,16) for v in (val[1:3], val[3:5], val[5:])]
                else:
                    pdb.set_trace()
                    raise ValueError("Incorrect arguments given to Color: {}".format(val))

            # Copy Color object
            elif isinstance(val, Color):
                # Create a copy via the RGBA values
                vals = (val.red(), val.green(), val.blue(), val.alpha())
                self._args = vals
            elif isinstance(val, QtGui.QColor):
                vals = (val.red(), val.green(), val.blue(), val.alpha())
                self._args = vals
            # Qt color enum
            elif isinstance(val, QtCore.Qt.GlobalColor):
                self._args = val
                return QtGui.QColor.__init__(self, val)
            else:
                raise ValueError("Incorrect arguments given to Color: {}".format(val))

        # Check for RGB or RGBA specifications
        elif len(args) == 4 or len(args) == 3:
            vals = args
            # Check for floats, and convert to Ints
            if float in [type(v) for v in vals] and max(vals) <= 1.0:
                # Convert to integer
                vals = [v*255 for v in vals]
            self._args = vals
        else:
            raise(TypeError, "Wrong type of args for Color: {}", args)
            pdb.set_trace()
            return None

        try:
            vals == 4
        except:
            pdb.set_trace()
            raise

        if len(vals) == 4:
            r, g, b, a = vals
        elif len(vals) == 3:
            r, g, b = vals
            if alpha is None:
                a = 255
            else:
                # Convert alpha to a float
                if type(alpha) is float and alpha <= 1.0:
                    alpha = 255*alpha
                a = alpha
        else:
            raise(TypeError, "Wrong type of args for Color: {}", args)

        QtGui.QColor.__init__(self, r, g, b, a)

        if alpha is not None:
            self.setAlpha(alpha)

    def __cmp__(self, other):
        return True

    @classmethod
    def yaml_representer(cls, dumper, data):
        tag = u"!Color"
        r = data.red()
        g = data.green()
        b = data.blue()
        a = data.alpha()
        if type(data._args) is str:
            return dumper.represent_sequence(tag, [data._args])
        else:
            return dumper.represent_sequence(tag, [r,g,b,a])

    @classmethod
    def yaml_constructor(cls, loader, node):
        values = loader.construct_sequence(node)
        try:
            return Color(*values)
        except:
            pdb.set_trace()
            raise

    def __repr__(self):
        r = self.red()
        g = self.green()
        b = self.blue()
        a = self.alpha()

        return u"Color({},{},{},{})".format(r,g,b,a)
yaml.add_representer(Color, Color.yaml_representer)
yaml.add_constructor('!Color', Color.yaml_constructor)