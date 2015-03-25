from ..base_component import BaseComponent

import os

class Simulation(BaseComponent):

    def __init__(self, parent=None, children=None, name='Simulation', params=None, measurements=None, work_dir=".",
                 log_file=None, disk_mgr=None, parallel=False):
        super().__init__(parent=parent, children=children, name=name, params=params, measurements=measurements,
                work_dir=work_dir, log_file=log_file, disk_mgr=disk_mgr, parallel=parallel)

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

    def create_netlist(self, file_name="netlist.cir"):
        if not os.path.isdir(self.work_dir):
            os.mkdir(self.work_dir)

        path = os.path.join(self.work_dir, file_name)
        self.netlist = path
        with open(path,'w') as netlist:
            netlist.write(self._netlist())
        return True

    def _run(self):
        self._create_netlist()
        self.results_file = os.path.join(self.work_dir, "output.txt")
        self.log_file = os.path.join(self.work_dir, "sim.log")
        cmd = "{sim} -o {out} -a".format(sim=self.simulator_path, out=self.results_file)
        result = subprocess.call([self.simulator_path, "-l", self.log_file, "-o", self.results_file, self.netlist])
        #print("Result:", result)
        if result == 0:
            try:
                self.results = self.load_results()
            except FileNotFoundError:
                print("No results for:", self.work_dir)

                raise