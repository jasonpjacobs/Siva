from ..base_component import BaseComponent
class Simulation(BaseComponent):

    def netlist(self):
        txt = []

        if self.__doc__:
            txt.append("* {}".format(self.__doc__))
        else:
            txt.append("* Simulation")

        for dict_name in ['include', 'libraries']:
            dct = getattr(self, dict_name)
            for item in dct.values():
                txt.append(item.card())
        return txt
