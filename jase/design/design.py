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


