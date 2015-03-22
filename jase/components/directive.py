import inspect
from .registered import Registered
from .component import Component

class Directive(Component):
    """ Used to implement declarative style directives during Component class definitions.

    This is similar in use to a Registered attribute, however, since the resulting instance isn't
    assigned to a class attribute, it isn't provided to the ComponentMeta class instance during
    class definition.

    During initialization, the Directive inspects the stack frame and inserts itself into
    a specific list (_directives) that is part of the Class name space.  The ComponentMeta class
    searches this list for directives, and calls their register method.

    class Option(Directive):
        dict_name = "options"

    class A(Component):
        # The following Option instance will be stored in the A.options dictionary.
        Option(name="mode", value="Fast")

    a = A()

    assert "data" in a.include
    """

    def __init__(self):
        frame = inspect.currentframe()
        f_locals = frame.f_locals

        # Need to go back through the stack frames to find the frame of the
        # parent component where this directive is instantiated.
        #
        # If self is subclassed its ancestors will be instances of the Directive class.
        while True:
            if 'self' in f_locals and isinstance(f_locals['self'], Directive):
                frame = frame.f_back
                f_locals = frame.f_locals
            else:
                break

        if '_directives' not in f_locals:
            f_locals['_directives'] = []
        f_locals['_directives'].append(self)

    def _store(self, class_dct=None, registry_name=None):
        self._store_as_list(class_dct=class_dct, registry_name=registry_name)
