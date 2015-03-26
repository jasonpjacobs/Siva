import os
import subprocess
import struct
import pdb

import numpy as np

from ..base_component import BaseComponent

class Simulation(BaseComponent):

    simulator_path = None

    def __init__(self, parent=None, children=None, name='Simulation', params=None, measurements=None, work_dir=".",
                 log_file=None, disk_mgr=None, parallel=False):

        assert self.simulator_path is not None

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
        return "\n".join(txt)


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
        self.netlist_path = path
        with open(path,'w') as netlist:
            netlist.write(self.netlist())
        return path

    def execute(self):
        """

        """
        self.info("Starting simulation.")
        self.create_netlist()
        self.results_file = os.path.join(self.work_dir, "output.raw")
        self.log_file = os.path.join(self.work_dir, "sim.log")

        result = subprocess.call([self.simulator_path, "-l", self.log_file, "-o", self.results_file, self.netlist_path])

        if result == 0:
            self.info("Simulation finished.")
            try:
                self.sim_results = self.load_results()
            except FileNotFoundError:
                print("No results for:", self.work_dir)

                raise
        else:
            self.error("Simulation error")

    def load_results(self, format="binary"):
        if format == "binary":
            bytes_read = open(self.results_file, "rb").read()

            marker = bytes('Binary:\n', "utf-8")
            start = bytes_read.find(marker) + len(marker)
            header = str(bytes_read[:start])
            lines = header.split("\\n")
            data = bytes_read[start:]

            size = len(data)/len(struct.pack('d',0.0))
            format = "{}d".format(int(size))

            # Parse the header to get wave names, number of vars and points
            headers = {}
            VARS_FOUND = False
            data_format = None
            for line in lines:
                if line == "Binary:":
                    break
                elif "No. Variables:" in line:
                    num_vars = int(line.split(":")[1])
                elif "No. Points:" in line:
                    try:
                        num_points = int([l for l in lines if "No. Points" in l][0].split(":")[1])
                    except ValueError:
                        # XYCE doesn't always fill in this field
                        num_points = None
                elif "Flags:" in line:
                    data_format = line.split(":")[1].strip()
                elif line == "Variables:":
                    VARS_FOUND = True
                    continue
                elif VARS_FOUND:
                    txt = line.replace("\\t", " ")
                    n, name, sig_type = txt.split()
                    headers[int(n)] = (int(n), name, sig_type)
                else:
                    continue

            if data_format == "real":
                cols_per_value = 1
            elif data_format == "complex":
                cols_per_value = 2
            else:
                print("ERROR:  XYCE results file wasn't formatted properly")
                pdb.set_trace()

            try:
                array = np.array(struct.unpack(format, bytes(data)))
            except:
                raise
                pdb.set_trace()


            if num_points is None:
                num_points = int(len(array)/(num_vars*cols_per_value))

            data = array.reshape((num_points, num_vars*cols_per_value))
            results = {}
            for n in headers:
                n, name, sig_type = headers[n]
                if data_format == "real":
                    results[name] = data[:,n]
                else:
                    results[name] = data[:,2*n] + data[:,2*n+1]*1j
            return results

