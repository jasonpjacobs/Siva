

import sys
import os
import h5py
import numpy as np

from ..wave import Wave

class Results(h5py.File):
    """ A wrapper around an HDF5 data set that stored simulation results.

    HDF5 is a hierarchical dataset that can store data as tables, vectors and scalers.  This class
    provides an interface to the HDF5 format that is streamlined for storage of signal/waveform data
    that is output from logic, circuit, and system simulators.

    For simulation results with a shared index (Spice, Matlab simulations) the waveform's
    x-data is a link to a vector at the root of the datastore.

    analysis_name (ac, dc, tran, etc)
        time: [x_values]
        root (top level DUT) (groups):
            instance_name (group)
                instance_name (group)
                    net (group):
                    pin (group):
                        v: [y_values, y_values]
                        i: [y_values]
                        time: --> (Link to /time)
                    node
                        y: [y_values]


    For simulation results from even driven simulations X, and Y values are stored
    for each signal, since the X values are not shared amongst signals.

    analysis_name (ac, dc, tran, etc)
        root (top level DUT)
            instance_name
                instance_name
                    net
                        v: [y_values]
                        time: [x_values]
    """

    _analyses = ['op', 'dc', 'ac', 'tran', 'vars']

    def __init__(self, path=None, mode='r', *args, **kwargs):
        if path is None:
            raise ValueError("No filename given for Results database.")

        super().__init__(path, mode, *args, **kwargs)

        self.current_analysis = None


    def select(self, name):
        if name not in self._analyses:
            raise ValueError("Analysis {} is not supported.")

        self.current_analysis = name
        if name in self:
            self.current_group = self[name]
        else:
            self.create_group(name)



    def add_waveform(self, path, x, y, y_name="y", x_name="x", attrs=None):
        """Adds waveform data to the results database.

        Waveforms must have an X and a Y component.  The Y component may have
        multiple columns.  A dictionary describing the attributes of this waveform
        can be supplied.

        For waveform databases that share the same index (Spice simulations, for example)
        an h5py Dataset can be supplied and a softlink will be used for the x component.
        """

        root = self[self.current_analysis]
        group = self.create_path(path)

        group[y_name] = y
        group[x_name] = x

        if attrs is None:
            attrs = {"type": "waveform",
                     "index" : x_name}
        else:
            if "type" not in attrs:
                attrs["type"] = "waveform"
                attrs["index"] = x_name

        for name, value in attrs.items():
            group[y_name].attrs[name] = value

        return group

    def add_vector(self, path, vector, name, attrs=None, index_name=None):
        root = self[self.current_analysis]
        group = self.create_path(path)

        group[name] = vector

        if attrs is None:
            attrs = {"type": "vector"}
        else:
            if "type" not in attrs:
                attrs["type"] = "vector"

        for attr_name, value in attrs.items():
            group[name].attrs[attr_name] = value

        return group

    def add_scalar(self, path, name, value, attrs=None):
        root = self[self.current_analysis]
        group = self.create_path(path)
        group[name] = value

        if attrs is not None:
            for attr_name, value in attrs.items():
                group[y_name].attrs[attr_name] = value


    def create_path(self, path):
        root = self[self.current_analysis]
        group = root.get(path)
        if group is None:
            group = root.create_group(path)
        return group

    # ---------------------------------------------------------
    #                      Access methods
    # ---------------------------------------------------------


    def get(self, path, analysis=None, name=None):
        if analysis is None:
            analysis = self.current_analysis

        root = self[analysis]

        if type(path) is str:
            # result.v("dut/i0/m1/g")
            group = root[path]
        elif hasattr(path, 'path_components'):
            # results.v(dut.i0.m1.g)
            group = "/".join(path.path_components())

        # Look up the dataset from the group
        x_ds = root[name]

        # Get it as Numpy array
        if x_ds.attrs['type'] == 'scalar':
            rv = x_ds.value
        elif x_ds.attrs['type'] == 'vector':
            rv = np.array(x_ds[:])

        elif x_ds.attrs['type'] == 'waveform':
            x = np.array(x_ds[:])
            y = group[x.attrs['index']]

            rv = Wave(x=x, y=y, name=node, interp='linear')
        return rv

    def v(self, node, analysis=None):
        self.get(node, analysis=analysis, results='v')

    def i(self, pin, analysis=None):
        self.get(node, analysis=analysis, results='v')

    def op(self, node, analysis=None):
        self.get(node, analysis=analysis, results='op')


