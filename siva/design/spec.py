"""

"""



from ..components.registered import Registered

class ResultMeta(type):
    """ Meta class to customize
    """
    def __eq__(self, other):
        """

        Allows the statement Pass == Marginal to return true.
        All other relationships return false.
        """
        return self.passed == other.passed

    def __repr__(self):
        return "{}".format(self.name)

class Result(metaclass=ResultMeta):
    passed = None

    def __init__(self, note=None):
        self.note = note

    def __eq__(self, other):
        return self.passed == other.passed

    def __repr__(self):
        return "{}".format(self.name)


class Pass(Result):
    """ All measurements have been taken meet specs.
    """
    name = "Pass"
    passed = True


class Marginal(Result):
    """The measurement has passed, but with little margin.
    """
    name = "Marginal"
    passed = True

class Fail(Result):
    """ One of the measurements does not pass its spec.
    """
    name = "Fail"
    passed = False


class Spec(Registered):
    registry_name = "specs"
    """Base class for specifications.  A specification is used to grade a measurement into
    a passed, failed, or marginal state.
    """

    def __init__(self, name=None, margin=None, conditions=None, units=None):
        self.name = name
        self.margin = margin
        self.conditions = conditions
        self.units = units

class Min(Spec):
    """ Asserts that the measurement is more than or equal to the given minimum.
    """
    def __init__(self, min, margin=0, name=None, conditions=None, units=None):
        super().__init__(name=name, margin=margin, conditions=conditions, units=units)
        self.min = min

    def eval(self, value):
        if (value >= self.min) and (value < (self.min + self.margin)) and self.margin != 0:
            return Marginal()
        elif value >= self.min:
            return Pass()
        else:
            notes = "value={}, expected >= {}".format(str(value), str(self.min))
            return Fail(note=notes)

class Max(Spec):
    """ Asserts that the measurement is less than or equal to the given maximum.
    """
    def __init__(self, max, margin=0, name=None, conditions=None, units=None):
        super().__init__(name=name, margin=margin, conditions=conditions, units=units)
        self.max = max

    def eval(self, value):
        if (value <= self.max) and (value < (self.max + self.margin)) and self.margin != 0:
            return Marginal()
        elif value <= self.max:
            return Pass()
        else:
            notes = "value={}, expected <= {}".format(str(value), str(self.max))
            return Fail(note=notes)

class Range(Spec):
    """ Asserts that the measurement is whihin the given range.
    """
    def __init__(self, range=None, min=None, max=None, margin=0, name=None, conditions=None, units=None ):
        super().__init__(name=name, margin=margin, conditions=conditions, units=units)

        if range is not None:
            if not(min is None and max is None):
                raise ValueError("Either range can be specified, or min/max, but not both.")

            self.range = range
        else:
            self.range = (min, max)

    def eval(self, value):

        result = Pass()
        if value <= self.max:
            if self.margin != 0 and value <= (self.max + self.margin):
                result = Marginal()
        else:
            result = Fail()

        if value >= self.min:
            if value < self.min + self.margin:
                return Marginal()
        else:
            result = Fail()

        return result

    @property
    def min(self):
        return self.range[0]

    @property
    def max(self):
        return self.range[1]

class Tolerance(Range):
    """ Asserts the measurement is withing a specified percentage or range of a target value.
    """
    def __init__(self, value, range=None, margin=0, conditions=None, units=None, name=None,
                 percent=None):
        super().__init__(name=name, margin=margin, conditions=conditions, units=units)

        self.value = value

        if range is not None:
            if not percent is None:
                raise ValueError("If *range* is specified, *percent* cannot also be specified.")

            if not hasattr(range, '__len__'):
                self.range = (self.value - abs(range), self.value + abs(range))
            elif len(range) == 2:
                self.range =  (self.value - abs(range[0]), self.value + abs(range[1]))
            else:
                ValueError("If *range* is specified, it must be one or two values.")
        elif percent is not None:
            if hasattr(percent, '__len__') and len(percent) == 2:
                self.range = (self.value * (1 - abs(percent[0]/100), self.value * (1 + percent[1])))
            else:
                self.range = (self.value * (1 - abs(percent)/100), self.value * (1 + percent/100))
        else:
            raise ValueError("Spec not correctly defined.")







