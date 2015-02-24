import collections

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
            new_copy[k] = copy.copy(v)
            if hasattr(v, 'parent'):
                v.parent = self
        return new_copy