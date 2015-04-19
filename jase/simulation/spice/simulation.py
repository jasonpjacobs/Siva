import os
import subprocess
import struct
import pdb

import numpy as np
import h5py

from ..base_component import BaseComponent, ExecutionError
from .save import Save
from ..base_component import Error

class Simulation(BaseComponent):

    simulator_path = None

    def __init__(self, parent=None, children=None, name='Simulation', params=None, measurements=None, work_dir=".",
                 log_file=None, disk_mgr=None, parallel=False):

        super().__init__(parent=parent, children=children, name=name, params=params, measurements=measurements,
                work_dir=work_dir, log_file=log_file, disk_mgr=disk_mgr, parallel=parallel)

        self.simulation_data = None

        self.results_file = "sim.raw"

    def validate(self):
        """Ensure the simulation is setup correctly before processing to the netlist/simulation phase
        """

        # Make sure an analysis was specified
        if not hasattr(self, 'analyses') or len(self.analyses) == 0:
            self.status = Error
            raise ValueError("Simulation need to have an analysis defined")

        # Make sure outputs are requested
        if not hasattr(self, 'saves') or len(self.saves) == 0:
            self.status = Error
            self.warn("No simulation outputs were requested")
            self.saves = []
            # raise ValueError("No simulation outputs were requested")


    def netlist(self):
        assert self.simulator_path is not None
        txt = []

        if self.__doc__:
            txt.append("* {}".format(self.__doc__.strip()))
        else:
            txt.append("* Simulation")
        txt.append('')

        if hasattr(self, 'includes') and self.includes:
            for include in self.includes:
                txt.extend(include.card())
            txt.append('')

        txt.append("** Analyses **")
        for analysis in self.analyses:
            txt.extend(analysis.card())
        txt.append('')

        if hasattr(self, 'sources'):
            txt.append("** Sources **")
            for source in self.sources.values():
                txt.extend(source.card())
            txt.append('')

        if hasattr(self, 'instances'):
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

        if hasattr(self,'saves'):
            txt.append("** Output Requests **")
            if self.saves:
                outputs = []
                for save in self.saves:
                    outputs.extend(save.outputs())
                card = Save.card(outputs, format='raw', analysis=self.analyses[0].analysis_name)
                txt.extend(card)

        if hasattr(self, 'options'):
            txt.append("** Options")
            for option in self.options:
                txt.extend(option.card())

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
        if not os.path.isdir(self._work_dir):
            os.mkdir(self._work_dir)

        path = os.path.join(self._work_dir, file_name)
        self.netlist_path = path
        with open(path,'w') as netlist:
            netlist.write(self.netlist())
            self._files.append(path)
        return path

    def execute(self):
        """ Runs a Spice simulation.

        Creates a netlist, then call

        """

        self.info("Starting simulation: {}".format(self.path))
        self.validate()
        self.create_netlist()
        self.log_file = os.path.join(self._work_dir, "sim.log")


        # The component is leaking file descriptors somewhere.  Perhaps the STDERR and STDOUT used by
        # the subprocess modeul are the problem.
        # Creating explicit STDERR and STDOUT files so they can be manually closed after the simulation is run.
        err_path = os.path.join(self._work_dir, "sim.err")
        out_path = os.path.join(self._work_dir, "sim.out")
        err_fp = open(err_path,'w')
        out_fp = open(out_path,'w')
        self.err_path = err_path
        self.out_path = out_path

        self._files.extend([self.results_file, self.log_file, self.err_path, self.out_path, self.netlist_path])
        try:
            # XYCE:
            # result = subprocess.check_output([self.simulator_path, "-l", self.log_file, "-o", self.results_file, self.netlist_path], stderr=subprocess.STDOUT)
            # NGspice
            """
            Need to take special care here on Windows machines:
            http://mihalop.blogspot.gr/2014/05/python-subprocess-and-file-descriptors.html

            """
            result = subprocess.check_output([self.simulator_path, "-b", "-o", self.log_file, "-r", self.results_file, self.netlist_path],
                                             stderr=err_fp, cwd=self._work_dir)

            pass
        except subprocess.CalledProcessError as e:
            msg = ["Simulation failed with error:", "    " +str(e.output), "    Return code: {}".format(e.returncode)]
            self.error("\n".join(msg))
            raise ExecutionError("Simulation failed: {}".format(self.path))
        finally:
            err_fp.close()
            out_fp.close()

        # Make sure simulation finished correctly
        try:
            assert os.path.exists(os.path.join(self._work_dir, self.results_file))
            assert os.path.getsize(os.path.join(self._work_dir, self.results_file)) > 0
        except AssertionError:
            raise
        self.info("Simulation finished: {}".format(self.path))
        try:
            self.sim_results = self.load_results(self.results_file, results_name=self.analyses[0].analysis_name.lower())
        except FileNotFoundError:
            self.error("No results for:", self._work_dir)
            raise ExecutionError("Results file not found.")
        except Exception:
            raise ExecutionError("Could not parse results: {}: {}/{}".format(self.path, self._work_dir, self.results_file))

    def load_results(self, results_file, output_file="sim.hdf5", results_name='tran'):
        """Reads the Python native, but simulator specific simulation results
        and converts it into a high level set of simulation results.
        """
        results_path = os.path.join(self._work_dir, results_file)
        assert os.path.exists(results_path)

        raw_data = self.load_raw_results(results_file)

        results = h5py.File(os.path.join(self._work_dir,output_file),'w-')

        root = results.create_group(results_name)     #Tran, AC, DC, etc

        results_name = self.analyses[0].analysis_name
        for entry in raw_data:

            # Entry will be either a keyword:  TIME, FREQ, V etc.
            if entry.lower() in ("time","frequency"):
                data = raw_data[entry]
                root['x'] = data

            if '(' in entry:
                (output_type, path, node) = self.parse_results_entry(entry)
                if not output_type in root:
                    root.create_group(output_type)
                group = root[output_type]

                full_path = "/".join(path + [node])
                group[full_path] = raw_data[entry]

        results.flush()
        self.simulation_data = results

    @staticmethod
    def parse_results_entry(entry):
        """ Exrancts output type, hierarchy, and node/net info from the labels in the results file.
        :param entry: V(XDUT.XI0.R1:p) --> (V, [dut, i0, r1], p)
        :return:
        """
        if '(' in entry:
            output_type = entry.split('(')[0]

            path = entry[entry.find("(")+1:entry.find(")")]

            if ":" in path:
                path, node_net = path.split(":")
            else:
                node_net = path
                path = ''

            if path is '':
                path = []
            elif "." in path:
                path = path.split('.')
            else:
                path = [path]

            orig_path = path
            path = []
            for name in orig_path:
                if name.startswith('X'):
                    name = name[1:]
                path.append(name.lower())

            return (output_type.lower(), path, node_net.lower())


    def load_raw_results(self, results_file, format="binary",):
        """Reads the raw simulation data and converts it into a low level, simulator specific,
        native Python format (Numpy arrays)
        """
        results_path = os.path.join(self._work_dir, results_file)
        if format == "binary":
            with open(results_path, "rb") as fp:
                bytes_read = fp.read()

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
                    """
                    Variables:
                    0	frequency	frequency	grid=3
                    1	v(g)	voltage
                    2	v(d)	voltage
                    3	v(s)	voltage
                    4	v(vdd)	voltage
                    5	v(m_dut#gate)	voltage
                    """
                    txt = line.replace("\\t", " ")
                    n, *rest = txt.split()
                    headers[int(n)] = (int(n), rest[0], rest[1])
                else:
                    continue

            if data_format == "real":
                cols_per_value = 1
            elif data_format == "complex":
                cols_per_value = 2
            else:
                self.error("Spice results file were not formatted properly. ({})".format(self.path))
                raise ValueError("Spice results were not formatted correctly.")

            try:
                array = np.array(struct.unpack(format, bytes(data)))
            except:
                self.error("Cannot parse sim results: {}".format(self.path))
                raise

            if num_points is None:
                num_points = int(len(array)/(num_vars*cols_per_value))

            try:
                data = array.reshape((num_points, num_vars*cols_per_value))
            except:
                raise
            results = {}
            for n in headers:
                n, name, sig_type = headers[n]
                if data_format == "real":
                    results[name] = data[:,n]
                else:
                    results[name] = data[:,2*n] + data[:,2*n+1]*1j
            return results


    def clean(self):
        if self.simulation_data:
            self.simulation_data.close()
        #del(self.simulation_data)
        super().clean()
