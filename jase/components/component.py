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

from .registered import Registered, ComponentDict

class ComponentMeta(type):
    """Meta class for all Components.  This metaclass will allow
    Parameters and child Components to be defined via declarative
    syntax.

    """
    def __new__(cls, name, bases, dct):
        dct['_component_dicts'] = []

        # Go through the instances created during class definition
        # and handle any items that request registration

        # dct will get appended to while iterating over it, so we need
        # to make a copy before iteration
        items = [(k,v) for k,v in dct.items()]
        for name, item in items:
            if hasattr(item,'register'):
                item.register(parent=cls, class_dct=dct, name=name)
        return super().__new__(cls, name, bases, dct)

class Component(Registered, metaclass=ComponentMeta):
    """
    Features:
    * Dotted path description and resolution
    * Component search: Find instances or attributes with desired tags
    * Declarative syntax
    * Eval contexts for scripting
    * New methods that create new instances of child components when an instance is created.
    """
    # Instance dicts to copy when cloning


    dict_name = "components"

    def __new__(cls, *args, **kwargs):
        inst = super().__new__(cls)

        """
        When defined as part of a Component class definition, child components, parameters,
        and other attributes are stored in the class dictionary.

        In order to prevent instance modification from affecting the class definition,
        we create copies of these items.
        """
        for dict_name in cls._component_dicts:
            # Get the original dict from the class
            comp_dict = getattr(cls, dict_name)

            # Create a copy
            inst_dict = comp_dict.clone(owner=inst)

            # Add it to the instance
            setattr(inst, dict_name, inst_dict)

        return inst

    if False:
        def register(self, parent, name, class_dct, key=None):
            """Called by the Component metaclass to add child Components
            to the class's *dict_name* dictionary
            """
            if name is not None:
                self.name = name

            self.parent = parent

            if key is None:
                dict_name = self.__class__.dict_name
            else:
                dict_name = key

            if dict_name not in class_dct:
                class_dct[dict_name] = ComponentDict(owner=parent)

            self._store(class_dct[dict_name])


        def _store(self, dct):
            self._store_as_value(dct)

        def _store_as_value(self, dct):
            dct[self.name] = self

        def _store_as_list(self, dct):
            if self.name not in dct:
                dct[self.name] = []
            dct[self.name].append(self)

        def _store_as_dict(self, dct, key):
            if self.name not in dct:
                dct[self.name] = {}
            dct[key] = self

        def XXregister(self, parent, dct, name=None):
            """Called by the Component metaclass to add child Components
            to the class's "component" dictionary prior to calling
            the class's __new__ method.
            """
            if name is not None:
                self.name = name

            self.parent = parent
            dct["components"][self.name] = self

    def clone(self, clone_inst=None, **kwargs):
        """ Create a clone of self.

        If 'orig' is provided, it will be made into a clone of self. Otherwise a new instance is created.
        """
        if clone_inst is None:
            clone_inst = self.__class__(name=self.name)

        #clone_inst.components = ComponentDict(owner=clone_inst)
        #clone_inst.params = ComponentDict(owner=clone_inst)

        for dict_name in self._component_dicts:
            inst_dict = ComponentDict(owner=clone_inst)
            setattr(clone_inst, dict_name, inst_dict)
            class_dct = getattr(self, dict_name)

            for name, item in class_dct.items():
                if hasattr(item, 'clone'):
                    inst_item = item.clone()
                else:
                    inst_item = copy.copy(item)
                inst_item.parent = clone_inst
                inst_dict[item.name] = inst_item

        # Other attributes can simply be reassigned w/o copying
        for k,v in self.__dict__.items():
            if k not in self._component_dicts and not k.startswith('_'):
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
                self.add_instance(child)

    @property
    def children(self):
        return self.components.values()

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
        from this component's point of view.
        """
        ns = {}

        if self.parent:
            ns.update(self.parent.hierarchy_namespace)

        ns.update(self.namespace)
        return ns

    @property
    def hierarchy_params(self):
        params = collections.OrderedDict()

        if self.parent:

            params.update(self.parent.hierarchy_params)

        for p in self.params.values():
            params[p.name] = p.value
        return params

    def __repr__(self):
        name = "{}(name={})".format(self.__class__.__name__, self.name)
        return name

    def add_instance(self, inst, name=None):
        if name is None:
            if hasattr(inst, 'name') and inst.name is not None:
                name = inst.name
            else:
                name = "i" + str(len(self.components) + 1)
        inst.name = name
        inst.parent = self

        inst.register_from_inst(self, cls=self.__class__, name=name)
