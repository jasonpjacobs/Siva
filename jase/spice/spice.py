import pdb
import collections
import os
import inspect
import subprocess

from .command import Command
from .node import Node
from .analysis import Analysis

class SpiceDict(collections.OrderedDict):
    default_factor = Node

    def __init__(self, cls=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cls = cls
        self.parent = None

    def __getitem__(self, item):
        #print("Getting ", item)
        return super().__getitem__(item)

    def __missing__ (self, key):
        frame = inspect.currentframe()
        c_locals = frame.f_back.f_back.f_locals
        c_globals = frame.f_back.f_back.f_globals

        if key in c_globals or key in c_locals or key in __builtins__:
            raise KeyError(key)
        else:
            self[key] = default = Node(key)
            return default

class SpiceMetaclass(type):
    @classmethod
    def __prepare__(metacls, name, bases):
        dct = SpiceDict(cls=metacls)
        return dct

    def __new__(metacls, name, bases, dct):
        instance = super().__new__(metacls, name, bases, dct)
        return instance

    def __init__(metacls, name, bases, dct):
        super().__init__(name, bases, dct)

        if metacls.__dict__.get('_parse_params',True):
            metacls._primitives = collections.OrderedDict()
            for key, value in dct.items():
                if not key.startswith("_") and isinstance(value, Command):

                    if value.name is None:
                        value.name = key
                    metacls._primitives[key] = value

                    if isinstance(value, Analysis):
                        metacls.analysis = value


class Spice(metaclass=SpiceMetaclass):
    __props = ['analysis', 'included', 'saves', 'libs', 'instances', 'params']

    keywords = ("Save",)
    simulator_path = None

    def _netlist(self):
        txt = []
        if self.__doc__:
            txt.append("* {}".format(self.__doc__))
        txt.append("**************************************************************")

        commands = self._commands

        if 'INC' in commands:
            for lib in commands['INC']:
                txt.append(lib.card())

        if 'analyses' in commands:
            for analysis in commands['analyses']:
                txt.append(analysis.card())
        else:
            raise ValueError("No analysis specified.  Aborting netlisting")

        for prim in self._primitives.values():
            txt.append(prim.card())

        if 'saves' in commands:
            for save in commands['saves']:
                txt.append(save.card(format="RAW"
                ))
        else:
            raise ValueError("No analysis specified.  Aborting netlisting")

        txt.append(".END")
        return "\n".join(txt)


    def __init__(self, work_dir=None, name="circuit", clean=False):
        self.work_dir = work_dir
        self.name = name

        if clean:
            self.clean_results()

    def clean_results(self):
        import shutil
        if os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir)
            os.mkdir(self.work_dir)



    @property
    def analysis(self):
        return self._analysis

    @analysis.setter
    def analysis(self, value):
        self._analysis = value

    def _create_netlist(self, file_name="netlist.cir"):
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
        print("Result:", result)
        if result == 0:
            self.results = self.load_results()


    def _post_process(self):
        pass


    def save(self, *args):
        self.analysis.save(*args)

    def Include(self):
        pass

