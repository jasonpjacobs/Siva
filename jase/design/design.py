from ..components.component import Component, ComponentMeta, ComponentNamespace
from .connections import Net

class DesignMeta(ComponentMeta):
    @classmethod
    def __prepare__(metacls, name, bases):
        return ComponentNamespace(default=Net)

class Design(Component, metaclass=DesignMeta):
    registry_name = "instances"

    def __init__(self, *conns, **params ):
        self.name = params.pop('name', None)

        for i, port in enumerate(self.ports.values()):
            if i < len(conns):
                port.connect(conns[i])

        for k,v in params.items():
            if k in self.ports:
                self.ports[k].connect(v)
            elif k in self.params:
                self.params[k].value = v
            else:
                raise ValueError("Instance argument '{}' is not a pin or a parameter of {}".format(k, self))

    @property
    def cell_name(self):
        return self.__class__.__name__

    def instance_designs(self, dct=None):
        """Returns a dictionary whose key are the cell names and whose value is a list of
        all instances in the design hierarchy"""
        if dct is None:
            dct = {}
        for inst in self.instances.values():
            name = inst.cell_name
            if name in dct:
                dct[name].append(inst)
            else:
                dct[name] = [inst]
            dct = inst.instance_designs(dct)
        return dct


