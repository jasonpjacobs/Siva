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
import copy

from ..types import Typed
from ..types.hierarchy import Node as TreeNode

class ComponentBase:
    ...

from .parameter import Parameter

class ComponentDict(collections.OrderedDict):
    def __init__(self, owner, *args, **kwargs):
        self.owner = owner
        super().__init__(*args, **kwargs)

    """
    def __missing__(self, key):
        if self.owner.parent is not None:
            print("{} missing from {}.  Asking {}".format(key, self.owner, self.owner.parent))
            return self.owner.parent._namespace[key]
    """
    def __deepcopy__(self, memo):
        new_copy = self.__class__(owner=self.owner)
        for k,v in self.items():
            new_copy[k] = copy.deepcopy(v, memo)
        return new_copy

class ComponentMeta(type):
    """Meta class for all Components.  This metaclass will allow
    Parameters and child Components to be defined via declarative
    syntax.

    """
    def __new__(cls, name, bases, dct):
        _components = ComponentDict(owner=cls)
        _params = ComponentDict(owner=cls)

        for k,v in dct.items():
            if k.startswith('_'):
                continue
            if isinstance(v, ComponentBase):
                if not hasattr(v, 'name'):
                    v.name = k
                    v.parent = cls
                _components[k] = v

            if isinstance(v, Parameter):
                if not hasattr(v, 'name'):
                    v.name = k
                    v.parent = cls
                _params[k] = v

        # Add this component dictionary to the class's namespace
        dct['_components'] = _components
        dct['_params'] = _params
        return super().__new__(cls, name, bases, dct)

class Component(ComponentBase, metaclass=ComponentMeta):
    """
    Features:
    * Dotted path description and resolution
    * Component search: Find instances or attributes with desired tags
    * Declarative syntax
    * Eval contexts for scripting
    * New methods that create new instances of child components when an instance is created.
    """

    def __new__(cls, *args, **kwargs):
        inst = super().__new__(cls)
        inst._components = ComponentDict(owner=inst)
        inst._params = ComponentDict(owner=inst)

        # Create copies of the components and parameters in the class dictionary,
        # so instance attribute lookup won't fall back to the attribute in the class dict.
        for comp_name in cls._components:
            comp_inst = copy.deepcopy(cls._components[comp_name])
            comp_inst.parent = inst
            inst._components[comp_name] = comp_inst

        for param_name in cls._params:
            param_inst = copy.deepcopy(cls._params[param_name])
            param_inst.parent = inst
            inst._params[param_name] = param_inst
        return inst

    def __init__(self, parent=None, children=None, name=None):
        self.name = name
        self.parent = parent
        if children is not None:
            self._components.update(children)
            for child in self.children.values():
                child.parent = self

    @property
    def children(self):
        return self._components

    @property
    def root(self):
        if self.parent is not None:
            return self.parent.root
        else:
            return self

    @property
    def path(self):
        if self.parent is not None:
            return self.parent.path + "." + str(self.name)
        else:
            return str(self.name)

    @property
    def path_components(self):
        if self.parent is not None:
            path =  self.parent.path_components
            path.append(self)
            return path
        else:
            return [self]

    @property
    def namespace(self):
        """ Returns a dictionary of the Component's non-local Parameter's name and value.

        This dictionary can be used as the locals() dict for expressions.
        """
        ns = {}
        if self.parent is not None:
            ns.update(self.parent.namespace)

        for var in self._params.values():
            if not var.local:
                ns[var.name] = var.value

        ns[self.name] = self
        return ns

    def __repr__(self):
        if hasattr(self, 'name'):
            name = self.name
        else:
            name = None
        if name is None:
            name = "{}()<@{}>".format(self.__class__.__name__, id(self))
        return name

    def __getattribute__(self, name):
        """Overridden to ensure that the Component's '_components' and '_params' dict
        is searched before the Class dictionary during attribute lookup
        """
        if name in ComponentBase.__getattribute__(self, '_components'):
            return ComponentBase.__getattribute__(self, '_components')[name]
        elif name in ComponentBase.__getattribute__(self, '_params'):
            return ComponentBase.__getattribute__(self, '_params')[name]
        else:
            return ComponentBase.__getattribute__(self, name)

    def add_instance(self, inst, name=None):
        if name is None:
            if hasattr(inst, 'name'):
                name = self.name
            else:
                name = "i" + str(len(self._components) + 1)
                inst.name = name
        inst.parent = self
        self._components[name] = inst

