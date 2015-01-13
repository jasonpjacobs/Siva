from weakref import WeakKeyDictionary

class Type:
    pass

class Variable(Type):
    def __init__(self, default=None):
        self.default = default
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance, self.default)

    def __set__(self, instance, value):
        assert value is not None, "Variables must be defined"
        self.data[instance] = value

class Int(Type):
    def __init__(self, default=None):
        self.default = default
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance, self.default)

    def __set__(self, instance, value):
        assert value is not None, "Variables must be defined"
        self.data[instance] = int(value)

class FloatType(Type):
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
    def __init__(self, default=None):
        self.default = default
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        value = self.data.get(instance, self.default)
        return value

    def __set__(self, instance, value):
        # Convert engineering notation ("10.5MEG") to floats
        if type(value) == str:
            value = self.str_to_float(value)
        self.data[instance] = value

    def str_to_float(self, string):
            string = string.replace(' ','')
            for unit in self.si_units:
                if unit in string:
                    string = string.replace(unit, self.si_units[unit])
            return float(string)


class BoolType(Type):
    def __init__(self, default=None):
        self.default = default
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance, self.default)

    def __set__(self, instance, value):
        self.data[instance] = bool(value)

class StringType(Type):
    def __init__(self, default=None, required=False):
        self.default = default
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance, self.default)

    def __set__(self, instance, value):
        self.data[instance] = str(value)

class EnumType(Type):
    def __init__(self, *choices, default=None):
        self.default = default
        self.choices = set(choices)
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance, self.default)

    def __set__(self, instance, value, cast=str):
        if value not in self.choices:
            raise ValueError("Value must be one of {}".format(self.choices))
        self.data[instance] = cast(value)

class NodeType(Type):
    def __init__(self, default=None):
        self.default=default
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance, self.default)

    def __set__(self, instance, value):
        assert value is not None, "Nodes must be defined"
        self.data[instance] = value
