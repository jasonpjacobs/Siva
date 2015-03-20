import collections
import copy
import inspect

class Registry(collections.OrderedDict):
    def __init__(self, owner=None, *args, **kwargs):
        self.owner = owner
        super().__init__(*args, **kwargs)

    def __deepcopy__(self, memo):
        new_copy = self.__class__(owner=self.owner)
        for k,v in self.items():
            new_copy[k] = copy.deepcopy(v, memo)
        return new_copy

    def clone(self, owner=None):
        if owner is None:
            owner = self.owner
        new_copy = self.__class__(owner=owner)
        for k,v in self.items():
            if hasattr(v, 'clone'):
                copied_item = v.clone()
            else:
                copied_item = copy.copy(v)
            new_copy[k] = copied_item
            if hasattr(v, 'parent'):
                copied_item.parent = owner
        return new_copy

class ListRegistry(list):
    def __init__(self, *args, owner=None):
        super().__init__(*args)
        self.owner = owner

    def clone(self, owner):
        new_copy = ListRegistry([copy.copy(item) for item in self], owner=owner)
        return new_copy

class Registered:
    registry_type = "dict"
    """A mix-in class to allow subclasses to register themselves when instantiated in
    a
    their parent's class definition
    """
    def register(self, parent, name=None, class_dct=None, key=None):
        """Called by the Component metaclass to add child Components
        to the class's *registry_name* dictionary

        E.g.:

            class Var(Registered):
                registry_name = "my_vars"

            class A(Component):
                v = Variable()  # "Variable" descends "from Registered"

            a = A()

            a[my_vars]['a'] == v

        When the definition for class A is executed, the metaclass for A will call v's "register" method.
        After being defined, class A will have an attribute named "my_vars",
        which will have an entry mapping the name "v" to the Variable instance "v".
        """
        self.parent = parent

        if name is not None:
            self.name = name

        if key is None:
            registry_name = self.__class__.registry_name
        else:
            raise NotImplementedError
            #registry_name = key

        """
        if registry_name not in class_dct:
            # When called from an inst, should use:  setattr(cls, registry_name, ComponentDict(owner=parent))
            try:
                if self.__class__.registry_type == "list":
                    class_dct[registry_name] = []
                else:
                    class_dct[registry_name] = Registry(owner=parent)
            except:
                pass

        """

        self._store(class_dct, registry_name)

        if registry_name not in class_dct['_registries']:
            class_dct['_registries'].append(registry_name)

    def register_from_inst(self, parent, name, cls, key=None):
        """ Handles component registration when child components are added to a component
        via the add_instance method.

        """
        self.parent = parent

        if name is not None:
            self.name = name

        if key is None:
            registry_name = self.__class__.registry_name
        else:
            registry_name = key

        # Add ourselves to the class dictionary
        setattr(cls, self.name, self)

        # The various store methods are designed to work with the class namespace dictionary
        # that is created by the metaclass during class construction.  When the class is already
        # created, we need to access/add attributes via getattr, setattr.
        #
        # To make this work, we'll pass in a local dictionary and update the instance with
        # the registry, after the _store method completes.

        ns = dict()
        if hasattr(parent, registry_name):
            ns[registry_name] = getattr(parent, registry_name)
        registry = self._store(ns, registry_name)
        if registry_name in ns:
            setattr(parent, registry_name, ns[registry_name])

        if registry_name not in cls._registries:
            cls._registries.append(registry_name)

    def _store(self, class_dct, registry_name):
        self._store_as_key_value_pair(class_dct, registry_name)

    def _store_as_key_value_pair(self, class_dct, registry_name):
        """ The registered component is stored in a dictionary


        parent_dct["registry_name"][self.name] = self

        E.g.:
        parent_dct["instances"]["a1"] = A()
        """
        if registry_name not in class_dct:
            class_dct[registry_name] = registry = Registry(owner=self.parent)
        else:
            registry = class_dct[registry_name]

        registry[self.name] = self

    def _store_as_list(self, class_dct, registry_name, ):
        """
        parent_dct["registry_name"] = [self, ...]

        E.g.:
        parent_dct["includes"] = [ path1, path2, path3,...]
        """
        if registry_name not in class_dct:
            class_dct[registry_name] = registry = ListRegistry(owner=self.parent)
        else:
            registry = class_dct[registry_name]
        registry.append(self)

    def __set__(self, instance, value):
        dct = getattr(instance, self.__class__.registry_name)
        dct[self.name] = value

    def __get__(self, instance, owner):
        if instance is not None:
            dct = getattr(instance, self.__class__.registry_name)
        else:
            dct = getattr(owner, self.__class__.registry_name)
        return dct[self.name]

