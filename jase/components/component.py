"""
Class definitions for Components.  Components are used to describe systems composed of objects that have a hierarchical
relationship to one another and form connections to ports (or attributes).

The most obvious use for components are for creating a model of an electrical design. Subcircuits and primitives in
Spice, as well as modules in Verilog will be descendants of this Component class.

A less obvious use will be for defining a complex simulation suite.  The simulation analysis itself will be one
component.  Loops (over parameters, voltage, temperature), searches, and optimizations will also be defined as
components.

"""

from ..types import Typed
from ..types.hierarchy import Node as TreeNode

class ComponentMeta(type):
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

class Component(TreeNode):
    """
    Features
    * Dotted path description and resolution
    * Component search: Find instances or attributes with desired tags
    * Declarative syntax
    """

    def __init__(self, parent=None, children=None):
        super().__init__(parent=parent, children=children)
        pass
