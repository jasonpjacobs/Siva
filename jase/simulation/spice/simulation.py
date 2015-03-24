from ..base_component import BaseComponent
#from ...design.design import Design

class Simulation(BaseComponent):

    def netlist(self):
        txt = []

        if self.__doc__:
            txt.append("* {}".format(self.__doc__.strip()))
        else:
            txt.append("* Simulation")
        txt.append('')

        if self.includes:
            for include in self.includes:
                txt.extend(include.card())
            txt.append('')

        txt.append("** Analyses **")
        for analysis in self.analyses:
            txt.extend(analysis.card())
        txt.append('')

        txt.append("** Sources **")
        for source in self.sources.values():
            txt.extend(source.card())
        txt.append('')

        if self.instances:
            txt.append("** Instances **")
            for inst in self.instances.values():
                txt.extend(inst.card())
            txt.append('')

        txt.append("** Subcircuit Definitions **")
        for inst_list in self.instance_designs().values():
            if inst_list[0]:
                card = inst_list[0].subckt_card()
                if card:
                    txt.extend(inst_list[0].subckt_card())
        txt.append('')

        txt.append("** Output Requests **")
        if self.saves:
            for save in self.saves:
                txt.extend(save.card())

        txt.append('')
        txt.append('.END')
        return txt


    def instance_designs(self, dct=None):
        """Returns a dictionary whose key are the cell names and whose value is a list of
        all instances in the design hierarchy"""
        if dct is None:
            dct = {}

        if not self.instances:
            return dct

        for inst in self.instances.values():
            name = inst.cell_name
            if name in dct:
                dct[name].append(inst)
            else:
                dct[name] = [inst]
            dct = inst.instance_designs(dct)
        return dct