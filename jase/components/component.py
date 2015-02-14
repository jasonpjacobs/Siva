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
        components = ComponentDict(owner=cls)
        params = ComponentDict(owner=cls)

        for k,v in dct.items():
            if k.startswith('_'):
                continue
            if isinstance(v, ComponentBase):
                if not hasattr(v, 'name'):
                    v.name = k
                    v.parent = cls
                components[k] = v

            if isinstance(v, Parameter):
                if not hasattr(v, 'name'):
                    v.name = k
                    v.parent = cls
                params[k] = v

        # Add this component dictionary to the class's namespace
        dct['components'] = components
        dct['params'] = params
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
    _dicts = []

    def __new__(cls, *args, **kwargs):
        inst = super().__new__(cls)
        inst.components = ComponentDict(owner=inst)
        inst.params = ComponentDict(owner=inst)

        # Create copies of the components and parameters in the class dictionary,
        # so instance attribute lookup won't fall back to the attribute in the class dict.
        for comp_name in cls.components:
            comp_inst = copy.deepcopy(cls.components[comp_name])
            comp_inst.parent = inst
            inst.components[comp_name] = comp_inst

        for param_name in cls.params:
            param_inst = copy.deepcopy(cls.params[param_name])
            param_inst.parent = inst
            inst.params[param_name] = param_inst
        return inst


    def clone(self, clone_inst=None, **kwargs):
        """ Create a clone of self.

        If 'orig' is provided, it will be made into a clone of self. Otherwise a new instance is created.
        """
        if clone_inst is None:
            clone_inst = self.__class__()

        clone_inst.components = ComponentDict(owner=self)
        clone_inst.params = ComponentDict(owner=self)

        # Create copies of the components and parameters in the class dictionary,
        # so instance attribute lookup won't fall back to the attribute in the class dict.
        for comp_name in self.components:
            comp_inst = self.components[comp_name].clone()
            comp_inst.parent = clone_inst
            clone_inst.components[comp_name] = comp_inst

        # Parameters need to copied seperately so their parent
        # attribute can be set
        for param_name in self.params:
            param_inst = copy.copy(self.params[param_name])
            param_inst.parent = clone_inst
            clone_inst.params[param_name] = param_inst

        # Other attributes can simply be reassigned w/o copying
        for k,v in self.__dict__.items():
            if k not in ('components', 'params') and not k.startswith('_'):
                setattr(clone_inst, k, v)

        # Apply new attribute values to the clone
        for name,value in kwargs.items():
            setattr(clone_inst, name, value)
        return clone_inst

    def __init__(self, parent=None, children=None, name=None):
        self.name = name
        self.parent = parent
        if children is not None:
            for child in children:
                self.components[child.name] = child
                child.parent = self

    @property
    def children(self):
        return self.components

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

        for comp in self.components.values():
            ns.update(comp.namespace)

        for var in self.params.values():
            if not var.local:
                ns[var.name] = var.evaluated_value

        for var in self.components.values():
            ns[var.name] = var

        ns[self.name] = self
        ns['self'] = self
        return ns

    @property
    def hierarchy_namespace(self):
        """Gets the name space for all components up the hierarchy,
        from this comppnent's point of view.
        """
        ns = {}

        if self.parent:
            ns.update(self.parent.hierarchy_namespace)

        ns.update(self.namespace)
        return ns

    @property
    def hierarchy_params(self):
        params = {}

        if self.parent:
            params.update(self.parent.hierarchy_params)
        params.update(self.params)
        return params

    def __repr__(self):
        name = "{}(name={})".format(self.__class__.__name__, self.name)
        return name

    def __getattribute__(self, name):
        """Overridden to ensure that the Component's '_components' and '_params' dict
        is searched before the Class dictionary during attribute lookup
        """
        if name in ComponentBase.__getattribute__(self, 'components'):
            return ComponentBase.__getattribute__(self, 'components')[name]
        # Removed to allow access to parameters via the descriptor protocol
        #elif name in ComponentBase.__getattribute__(self, 'params'):
        #    return ComponentBase.__getattribute__(self, 'params')[name]
        else:
            return ComponentBase.__getattribute__(self, name)

    def add_instance(self, inst, name=None):
        if name is None:
            if hasattr(inst, 'name') and inst.name is not None:
                name = inst.name
            else:
                name = "i" + str(len(self.components) + 1)
        inst.name = name
        inst.parent = self
        self.components[name] = inst

