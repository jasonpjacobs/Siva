from collections import OrderedDict

from siva.qt_bindings import Qt, QtGui


class Type:
    allow_formulas = True
    formula_prefix = '='
    def __init__(self,

        # Default value
        default=None,

        # A detailed description, used for mouse-over text in table and tree views
        desc=None,

        # A Python expression for the attribute's value
        formula=None,

        # If true, the attribute can be edited in tree, table views
        editable=True,

        # If true, will display a checkbox
        checkbox=False,

        # If true, will display a tri-state checkbox
        tristate=False,

        # Text to display as a tool tip
        tool_tip=None,

        # Qt editor to use, in place of the default
        editor=None,

        # Text formatting attributes
        font_color=None,
        bg_color=None,
        font=None,
        icon=None,
        italic=False,
        bold=False,
        strikeout=False,
        underline=False,

        # Validators are callables that receive a value and return True if the value is valid
        # and False if it is not
        validators=None,

        # Formatting
        formatter=None,

        # Built-in validators
        min = None,
        max = None,
        values = None

        ):

        # The attribute for which this descriptor is used.
        # The MetaType class will set this when the descriptor is
        # instantiated
        self.attr = None

        # A dict to store the per-instance attribute values
        #TODO: Use weakref dict?
        self.insts = {}

        if default is not None:
            self.default = default

        self.desc = desc  # Presented to the user as tool tips (if an explicit tool tip isn't available)

        # For formula based properties
        self.formula = formula

        # Used for Qt Model implementation
        self.editable = editable
        self.checkbox = checkbox
        self.tristate = tristate
        self.editor = editor
        self.icon = icon                # Decoration role
        self.tool_tip = tool_tip        # Tool tip role
        self.font = font                # Font role
        self.font_color = font_color    # Foreground role
        self.bg_color = bg_color        # Background role
        self.italic = italic            # Font role
        self.strikeout = strikeout      # Font role
        self.bold = bold                # Font role
        self.underline = underline      # Font role

        if formatter == None:
            formatter = str
        self.formatter = formatter

        # Validation
        if validators is not None:
            # Received a sequence
            if hasattr(validators, '__iter__'):
                if not hasattr(validators[0], '__call__'):
                    raise TypeError("Validator must be a callable or a list of callables")
                self.validators = validators
            # Received a callable
            elif hasattr(validators, '__call__'):
                    self.validators = [validators]
            else:
                raise TypeError("Validator must be a callable or a list of callables")
        else:
            self.validators = []

        # Convenience validation
        if min is not None:
            self.min = min
            self.validators.append(lambda x: x > self.min)

        if max is not None:
            self.max = max
            self.validators.append(lambda x: x < self.max)

        if values is not None:
            self.values = values
            self.validators.append(lambda x:  x in self.values)

    def __get__(self, instance, owner):
        return self.insts.get(instance, self.default)

    def __set__(self, instance, value):
        trial_value = self.cast(self.eval(value))
        if self.validate(trial_value):
            self.insts[instance] = trial_value
        else:
            raise ValueError

    def eval(self, value, locals=None):
        if type(value) == str and self.allow_formulas and value[0] == self.formula_prefix:
            value = eval(value[1:])
        return value

    def cast(self, value):
        """Casts a new value to the expected data type
        """
        return value

    def validate(self, value):
        return True

    # ---------------------------------------------------------------------------------------------
    # Helper methods to simply appearance in Qt views
    # ---------------------------------------------------------------------------------------------
    @property
    def tool_tip(self):
        if self._tool_tip is not None:
            return self._tool_tip
        elif self.desc is not None:
            return self.desc
        else:
            return None
    @tool_tip.setter
    def tool_tip(self, value):
        self._tool_tip = value

    # Icon getter/setter
    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, value):
        self._icon = value

    #  Font color property
    @property
    def font_color(self):
        return self._font_color

    @font_color.setter
    def font_color(self, value):
        if value is None:
            self._font_color = None
        else:
            self._font_color = QtGui.QColor(value)

    #  Font  property
    @property
    def font(self):
        font = QtGui.QFont()
        if self.strikeout:
            font.setStrikeOut(True)
        if self.italic:
            font.setItalic(True)
        if self.bold:
            font.setBold(True)
        if self.underline:
            font.setUnderline(True)
        return font

    @font.setter
    def font(self, value):
        self._font = value

    @property
    def strikeout(self):
        return self._strikeout

    @strikeout.setter
    def strikeout(self, value):
        self._strikeout = value

    @property
    def italic(self):
        return self._italic

    @italic.setter
    def italic(self, value):
        self._italic = value

    @property
    def bg_color(self):
        return self._bg_color

    @bg_color.setter
    def bg_color(self, value):
        if value is None:
            self._bg_color = None
        else:
            self._bg_color = QtGui.QColor(value)

    # ---------------------------------------------------------------------------------------------
    #         Qt Model Interface
    # ---------------------------------------------------------------------------------------------
    def data(self, obj, locals=None):
        #if data is a link, evaluate the link


        # If data is a formula, evaluate it
        if self.formula is not None:
            value = self.eval(obj, locals)

        # Otherwise, just present the data as-is
        if not hasattr(obj, self.attr):
            return None
        value = getattr(obj, self.attr)
        if self.formula:
            value = self.eval(obj, locals)

        if value is None:
            return ""

        if self.formatter is not None:
            string = self.formatter(value)
        else:
            string = value
        return string

    def checkState(self, obj):
        if hasattr(obj, self.attr) and self.checkbox is True:
            value = getattr(obj, self.attr)
            value = self.cast(value)
            if value is True:
                return Qt.Checked
            else:
                return Qt.Unchecked
        return None

    def setData(self, obj, value):
        c_value = self.cast(value)
        result = self.validate(c_value)
        if result:
            setattr(obj, self.attr, c_value)
        return result

    def flags(self, obj):
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

        if self.editable:
            flags |= Qt.ItemIsEditable

        if self.checkbox:
            flags |= Qt.ItemIsUserCheckable

        if self.tristate:
            flags |= Qt.ItemIsTristate
        return flags

    # --------------------------------
    #  Methods to get color/font based on
    #  an objects values.
    # --------------------------------
    def getFont(self, obj):
        return self.font

    def getFontColor(self, obj):
        return QtGui.QColor(self.font_color)

    def getBGColor(self, obj):
        if self.bg_color:
            return QtGui.QColor(self.bg_color)
        return None

    def getIcon(self, obj):
        return self.icon


class Int(Type):
    default = 0

    def cast(self, value):
        return int(value)


class Str(Type):
    default = ''

    def cast(self, value):
        return str(value)


class Float(Type):
    default = .0
    si_units = {
        "f" : "e-15",
        "p" : "e-12",
        "n" : "e-9",
        "u" : "e-6",
        "m" : "e-3",
        "K" : "e3",
        "k" : "e3",
        "MEG" : "e6",
        "M" : "e6",
        "G"  : "e9",
        "g" : "e9",
        "T" : "e12",
        "t" : "e12"
    }

    def eval(self, value):
        value = super().eval(value)
        # Convert engineering notation ("10.5MEG") to floats
        if type(value) == str:
            value = self.str_to_float(value)
        return value

    def cast(self, value):
        return float(value)

    def str_to_float(self, string):
            string = string.replace(' ','')
            for unit in self.si_units:
                if unit in string:
                    string = string.replace(unit, self.si_units[unit])
            return float(string)

class Bool(Type):
    default = False
    checkbox = True

    def cast(self, value):
        if str(value).lower() in ("true", "false"):
            if str(value).lower() == "true":
                return True
            else:
                return False
        elif value == '0':
            return False
        else:
            return bool(value)



class DescriptorDict(OrderedDict):
    """An ordered dict that can be accessed by index or by name
    """
    pass

class MetaType(type):
    """This metaclass will parse the class *dct*, grabbing the descriptors from them
     to store in a separate _descriptor dictionary.  The Qt models will use this
     dictionary to map attributes of items in their models to Qt model data roles.
    """
    def __new__(cls, name, bases, dct):

        _descriptors = DescriptorDict()
        for base in bases:
            if '_descriptors' in base.__dict__:
                td = base.__dict__.get('_descriptors')
                for k,v in td.items():
                    _descriptors[k] = v

        for k,v in dct.items():
            if isinstance(v, Type):
                v.attr = k
                if not hasattr(v, 'name'):
                    v.name = k
                _descriptors[k] = v

        dct['_descriptors'] = _descriptors
        return super().__new__(cls, name, bases, dct)

class Typed(metaclass=MetaType):
    pass