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
        c_locals = frame.f_back.f_back.f_locals
        if '_directives' not in c_locals:
            c_locals['_directives'] = []
        c_locals['_directives'].append(self)

    def _store(self, class_dct=None, registry_name=None):
        self._store_as_list(class_dct=class_dct, registry_name=registry_name)
