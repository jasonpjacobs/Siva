from ..base_component import BaseComponent
class Simulation(BaseComponent):

    def netlist(self):
        txt = []

        if self.__doc__:
            txt.append("* {}".format(self.__doc__))
        else:
            txt.append("* Simulation")

        for registry_name in ['include', 'libraries']:
            registry = getattr(self, registry_name)
            if registry:
                for item in registry:
                    txt.append(item.card())
        return txt
