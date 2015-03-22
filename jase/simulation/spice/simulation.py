from ..base_component import BaseComponent
class Simulation(BaseComponent):

    def netlist(self):
        txt = []

        if self.__doc__:
            txt.append("* {}".format(self.__doc__))
        else:
            txt.append("* Simulation")
        txt.append('')

        for registry_name in ['include', 'libraries']:
            registry = getattr(self, registry_name)
            if registry:
                for item in registry:
                    txt.extend(item.card())

        txt.append("* Sources")
        for source in self.sources.values():
            txt.extend(source.card())
        txt.append('')

        txt.append("* Analyses")
        for analysis in self.analyses:
            txt.extend(analysis.card())
        txt.append('')

        txt.append("* Instances")
        for inst in self.instances.values():
            txt.extend(inst.card())

        return txt
