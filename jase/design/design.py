from ..components.component import Component, ComponentMeta, ComponentNamespace
from .connections import Net, Pin

class DesignMeta(ComponentMeta):
    @classmethod
    def __prepare__(metacls, name, bases):
        return ComponentNamespace(default=Net)

class Design(Component, metaclass=DesignMeta):
    registry_name = "instances"

    def __init__(self, *conns, **params ):
        self.name = params.pop('name', None)

        # Handle the case where port/net connections are passed in as arguments
        for i, port in enumerate(self.ports.values()):
            if i < len(conns):
                # If a string was passed in, convert it to a net and add it to our
                # parent
                if type(conns[i]) is str:
                    # TODO: Allow design instances to create nets for their parents
                    raise NotImplementedError('Defining nets via strings is not supported')
                    self.super_nets.append(Net(name=conns[i]))
                elif isinstance(conns[i], Pin):
                    net = conns[i].net
                else:
                    net = conns[i]
                port.connect(net)

        # Handle the cases where port/net connects, or parameter name/values
        # are passed in as keywords
        for k,v in params.items():
            if k in self.ports:
                if type(v) is str:
                    # TODO: Allow design instances to create nets for their parents
                    raise NotImplementedError('Defining nets via strings is not supported')
                    net = Net(name=v)
                    elf.super_nets.append(Net(name=conns[i]))
                elif isinstance(v, Pin):
                    net = v.conn
                else:
                    net = v
                self.ports[k].connect(net)
            elif k in self.params:
                self.params[k].value = v
            else:
                raise ValueError("Instance argument '{}' is not a pin or a parameter of {}".format(k, self))

    @property
    def cell_name(self):
        return self.__class__.__name__


    def add_net(self, name=None, net=None, overwrite=False):
        if name is None and net is None:
            raise ValueError("Either name or net arguments must be provided.")

        # If net already exists, do not overwrite it
        if overwrite is False and name in self.nets:
            return

        if net is None:
            net = Net(name=name)
        self.nets[name] = net
        return net

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

    @property
    def path(self):
        if self.parent is not None and isinstance(self.parent, Design):
            return self.parent.path + "." + str(self.name)
        else:
            return str(self.name)

    @property
    def path_components(self):
        if self.parent is not None and isinstance(self.parent, Design):
            path =  self.parent.path_components
            path.append(self)
            return path
        else:
            return [self]

