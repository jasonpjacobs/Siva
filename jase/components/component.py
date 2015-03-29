"""
Class definitions for Components.  Components are used to describe systems composed of objects that have a hierarchical
relationship to one another and form connections to ports (or attributes).

The most obvious use for components are for creating a model of an electrical design. Subcircuits and primitives in
Spice, as well as modules in Verilog will be descendants of this Component class.

A less obvious use will be for defining a complex simulation suite.  The simulation analysis itself will be one
component.  Loops (over parameters, voltage, temperature), searches, and optimizations will also be defined as
"""

import collections
import copy
import inspect

from .registered import Registered, Registry

class ComponentNamespace(collections.OrderedDict):
    """ A dictionary that provides instances of a default class
    for missing items in the class definition namespace.

    For example, when defining a Spice (simulation) component,
    undefined names will become Net instances.
    """
    def __init__(self, default=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Default is a class..
        if default is not None:
            assert(callable(default))
        self.default = default

    def __missing__ (self, key):
        # Get the locals and globals from the frame where the parent class is being defined
        frame = inspect.currentframe()
        c_locals = frame.f_back.f_back.f_locals
        c_globals = frame.f_back.f_back.f_globals

        # Only create defaults for names that would otherwise raise an
        # attribute error
        if key in c_globals or key in c_locals or key in __builtins__ or key.startswith('_') or key[0].isupper() :
            raise KeyError(key)
        else:
            val = self.get_default(name=key)
            print("Creating a {} for {}".format(val.__class__.__name__, key))
            self[key] = val
            return val

    def get_default(self, name):
        """Creates an instance of the default class.
        """
        if self.default is not None:
            return self.default(name)
        else:
            raise KeyError(name)

class ComponentMeta(type):
    """Meta class for all Components.  This metaclass will allow
    Parameters and child Components to be defined via declarative
    syntax.
    """

    @classmethod
    def __prepare__(metacls, name, bases):
        dict = ComponentNamespace()
        return dict

    def __new__(cls, name, bases, dct):
        registries = ['components', 'params']
        if len(bases) > 0:
            for base in bases:
                if hasattr(base, '_registries'):
                    for registry_name in base._registries:
                        registries.append(registry_name)
                        dct[registry_name] = getattr(base, registry_name).clone()

        dct['_registries'] = list(set(registries))

        # Ensure all components have at least 'components' and 'params' dicts
        if 'components' not in dct:
            dct['components'] = Registry(owner=cls)
        if 'params' not in dct:
            dct['params'] = Registry(owner=cls)

        # Go through the instances created during class definition
        # and handle any items that request registration

        # dct will get appended to while iterating over it, so we need
        # to make a copy before iteration
        items = [(k,v) for k,v in dct.items() if not k.startswith('_')]
        for item_name, item in items:
            if hasattr(item,'register'):
                item.register(parent=cls, class_dct=dct, name=item_name)

        for directive in dct.get('_directives', []):
            directive.register(parent=cls, class_dct=dct)
        return super().__new__(cls, name, bases, dict(dct))

class Component(Registered, metaclass=ComponentMeta):
    """
    Features:
    * Dotted path description and resolution
    * Component search: Find instances or attributes with desired tags
    * Declarative syntax
    * Eval contexts for scripting
    * New methods that create new instances of child components when an instance is created.
    """

    # When instantiated inside of a parent Component, instances will also be grouped
    # into a parents dict named 'dict_name'.
    registry_name = "components"

    def __new__(cls, *args, **kwargs):

        cls._args = args
        cls._kwargs = kwargs

        inst = super().__new__(cls)

        # When defined as part of a Component class definition, child components, parameters,
        # and other attributes are stored in the class dictionary.
        #
        # In order to prevent instance modification from affecting the class definition,
        # we create copies of these items.
        for registry_name in cls._registries:
            # Get the original dict from the class
            registry = getattr(cls, registry_name)

            # Create a copy
            try:
                inst_dict = registry.clone(owner=inst)
            except:
                raise

            # Add it to the instance
            setattr(inst, registry_name, inst_dict)

        # Make sure the instance knows its registries
        inst._registries = list(cls._registries)

        return inst

    def clone(self, clone_inst=None, **kwargs):
        """ Create a clone of self.

        If 'orig' is provided, it will be made into a clone of self. Otherwise a new instance is created.
        """
        if clone_inst is None:
            args = copy.copy(self._kwargs)
            args['name'] = self.name
            clone_inst = self.__class__(*self._args, **self._kwargs)

        for registry_name in self._registries:
            if not hasattr(self, registry_name):
                continue

            orig_registry = getattr(self, registry_name)
            inst_registry = orig_registry.clone(owner=clone_inst)
            setattr(clone_inst, registry_name, inst_registry)

        # Other attributes can simply be reassigned w/o copying
        for k,v in self.__dict__.items():
            if k not in self._registries and not k.startswith('_'):
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
        dct = getattr(self, self.__class__.registry_name)
        return dct.values()

    @property
    def root(self):
        if self.parent is not None:
            return self.parent.root
        else:
            return self

    @property
    def path(self):
        if self.parent is not None:
            return self.parent.path + "." + str(self.inst_name)
        else:
            return str(self.inst_name)

    @property
    def inst_name(self):
        if hasattr(self, '_inst_name') and self._inst_name is not None:
            return self._inst_name
        else:
            return self.name

    @inst_name.setter
    def inst_name(self, value):
        self._inst_name = value

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

    @property
    def _param_dict(self):
        """Returns the components parameters in a dictionary
        """
        dct = collections.OrderedDict()
        dct['name'] = self.name

        for param in self.params.values():
            dct[param.name] = str(param) if param.value is not None else None
        return dct

    def __getattr__(self, name):
        for registry_name in self._registries:
            registry = self.__getattribute__(registry_name)
            if name in registry:
                return registry[name]
        raise AttributeError

    def __repr__(self):
        name = "{}(name={})".format(self.__class__.__qualname__, self.name)
        return name

    def add_instance(self, inst, name=None):
        if name is None:
            if hasattr(inst, 'name') and inst.name is not None:
                name = inst.name
            else:
                name = "i" + str(len(self.components) + 1)
        inst.name = name
        inst.parent = self

        inst.register_from_inst(parent=self, name=name)
