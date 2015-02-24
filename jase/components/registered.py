import collections
import copy

class ComponentDict(collections.OrderedDict):
    def __init__(self, owner, *args, **kwargs):
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
            copied_item = copy.copy(v)
            new_copy[k] = copied_item
            if hasattr(v, 'parent'):
                copied_item.parent = owner
        return new_copy

class Registered:
    """A mix-in class to allow subclasses to register themselves when instantiated during
    their parent's class definition
    """
    def register(self, parent, name, class_dct=None, key=None):
        """Called by the Component metaclass to add child Components
        to the class's *dict_name* dictionary

        E.g.:

            class Var(Registered):
                dict_name = "my_vars"

            class A(Component):
                v = Variable()  # "Variable" descends "from Registered"

            a = A()

        When the definition for class A is executed, the metaclass for A will call v's "register" method.
        After being defined, class A will have an attribute named "my_vars",
        which will have an entry mapping the name "v" to the Variable instance "v".
        """
        self.parent = parent

        if name is not None:
            self.name = name

        if key is None:
            dict_name = self.__class__.dict_name
        else:
            dict_name = key

        if dict_name not in class_dct:
            # When called from an inst, should use:  setattr(cls, dict_name, ComponentDict(owner=parent))
            try:
                class_dct[dict_name] = ComponentDict(owner=parent)
            except:
                pass

        self._store(class_dct[dict_name])

        if dict_name not in class_dct['_component_dicts']:
            class_dct['_component_dicts'].append(dict_name)

    def register_from_inst(self, parent, name, cls, key=None):
        """ Handles component registration

            class Var(Registered):
                dict_name = "my_vars"

            class A(Component):
                v = Variable()  # "Variable" descends "from Registered"

            a = A()

        """
        self.parent = parent

        if name is not None:
            self.name = name

        if key is None:
            dict_name = self.__class__.dict_name
        else:
            dict_name = key

        if not hasattr(cls, dict_name):
            component_dict = ComponentDict(owner=parent)
            setattr(cls, dict_name, component_dict)
        else:
            component_dict = getattr(cls, dict_name)

        self._store(component_dict)

        if dict_name not in cls._component_dicts:
            cls._component_dicts.append(dict_name)

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

    def __set__(self, instance, value):
        dct = getattr(instance, self.__class__.dict_name)
        dct[self.name] = value

    def __get__(self, instance, owner):
        if instance is not None:
            dct = getattr(instance, self.__class__.dict_name)
        else:
            dct = getattr(owner, self.__class__.dict_name)
        return dct[self.name]

