"""
Class definitions for Components.  Components are used to describe systems composed of objects that have a hierarchical
relationship to one another and form connections to ports (or attributes).

The most obvious use for components are for creating a model of an electrical design. Subcircuits and primitives in
Spice, as well as modules in Verilog will be descendants of this Component class.

A less obvious use will be for defining a complex simulation suite.  The simulation analysis itself will be one
component.  Loops (over parameters, voltage, temperature), searches, and optimizations will also be defined as
components.

"""
import pdb

import collections

from ..types import Typed
from ..types.hierarchy import Node as TreeNode

class ComponentBase:
    ...

class ComponentParameter(ComponentBase):
    category = "params"
    pass

class ComponentDirective(ComponentBase):
    category = "directives"

class ComponentDict(collections.OrderedDict):
    def __init__(self, owner, *args, **kwargs):
        self.owner = owner
        super().__init__(*args, **kwargs)

    def __missing__(self, key):
        if self.owner.parent is not None:
            print("{} missing from {}.  Asking {}".format(key, self.owner, self.owner.parent))
            return self.owner.parent._namespace[key]

class ComponentMeta(type):
    """Meta class for all Components.  This metaclass will allow for closs
    definition via a declarative syntax, as well has sharing the name
    space up and down the component hierarchy.

    """
    def __new__(cls, name, bases, dct):
        _namespace = ComponentDict(owner=cls)

        """
        Implementation of the declarative definition
        will be deferred for now, but I'll leave this code here as a
        reminder.

        for base in bases:
            if '_descriptors' in base.__dict__:
                td = base.__dict__.get('_descriptors')
                for k,v in td.items():
                    _descriptors[k] = v


        """
        for k,v in dct.items():
            if isinstance(v, ComponentBase):
                print("Adding {} to namespace".format(v))
                v.attr = k
                if not hasattr(v, 'name'):
                    v.name = k
                _namespace[k] = v

        dct['_namespace'] = _namespace

        return super().__new__(cls, name, bases, dct)

class Component(TreeNode, ComponentBase, metaclass=ComponentMeta):
    """
    Features
    * Dotted path description and resolution
    * Component search: Find instances or attributes with desired tags
    * Declarative syntax
    """

    def __new__(cls, *args, **kwargs):
        print("New instance being created")
        inst = super().__new__(cls)





        return inst

    def __init__(self, parent=None, children=None):
        super().__init__(parent=parent, children=children)
        self._namespace = ComponentDict(owner=self)
        pass

