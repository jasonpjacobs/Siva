"""
http://www.vhdl.org/ibis/touchstone_ver2.0/touchstone_ver2_0.pdf
"""
import numpy as np
import pdb


class Touchstone:
    def __init__(self, filename=None, n=4):
        # Setup the defaults
        self.freq_unit = 'GHz'
        self.param = 'S'
        self.format = 'MA'
        self.R = 50
        self.two_port_data_order = '12_21'  # Default for v1.0
        self.num_freqs = None
        self.num_noise_freqs = None
        self.matrix_format = None

        self.names = []
        if filename is not None:
            self.n = n
            self.read(filename)

    def read(self, filename):
        data_lines = []
        with open(filename,'r') as f:
            for line in f.readlines():
                words = line.split(' ')
                if line[0] == '!':
                    continue
                elif line[0] == '#':
                    self.parse_options(line)
                elif '[' in line:
                    keyword, value = line.split(' ')
                    keyword = keyword[1:-1] # Remove brackets
                    self.parse_keyword(keyword, value)
                else:
                    data_lines.append(line)

        self.calculate_names()

        rows = self.group_data_lines(data_lines)
        freqs, ports = self.parse_rows(rows)
        self.freqs = freqs
        self.ports = ports


    def parse_keyword(self, keyword, value):
        """Parses the [Keyword] directive found in v2.0 file formats"""
        if keyword == "Version":
            self.version = float(value)
            assert (self.version > 1.0)
        if keyword == "Number of Ports":
            self.n = int(value)
        if keyword == "Number of Frequencies":
            self.num_freqs = int(value)
        if keyword == "Two-Port Data Order":
            # Signifies column ordering convention is v2.0 formatted files
            assert value in ( '12_21', '21_12')
            self.two_port_data_order = value
        if keyword == "Number of Noise Frequencies":
            self.num_noise_freqs = int(value)
        if keyword == "Reference" in line:
            self.r = float(value)
        elif keyword == "Matrix Format":
            assert value in ('Full', 'Lower', 'Upper')
            self.matrix_format  = value

    def parse_options(self, line):
        """ Parse the option line.  Options can appear in any order, but fairly restricted in what values
        they can take.  So, we just look for a match
        """
        GET_R = False

        # Split the line into tokens
        options = line.split()[1:]
        # Search
        for option in options:
            if GET_R:
                GET_R = False
                self.R = option
            elif option.upper() in ('HZ', 'KHZ', 'MHZ','GHZ'):
                self.freq_unit = option.upper()
            elif option in ('S', 'Y', 'Z', 'H', 'G'):
                self.param = option
            elif option in ('DB', 'MA', 'RI'):
                self.format = option
            elif option == 'R':
                self.GET_R = True
                continue


    def group_data_lines(self, lines):
        assert self.n is not None
        print(len(lines))

        # Only support 4-port files for now
        if self.n != 4:
            raise(NotImplementedError, "Only 4 port files can be read.")

        groups = []
        group = None
        for line in lines:
            tokens = line.split()
            if len(tokens) == 2*self.n + 1:
                # Append the previous group to the list of groups
                if group:
                    groups.append(group)

                # Start a new group with the current row
                group = [float(t) for t in tokens]
            else:
                group += [float(t) for t in tokens]

        # Add the last group
        if group:
            groups.append(group)
        return groups


    def parse_rows(self, rows):
        freqs = []
        ports = {}
        ports[0] = None
        for i in range(len(self.names)):

            ports[self.names[i]] = []

        formatter = {
            'DB' : self.format_db,
            'MA' : self.format_ma,
            'RI' : self.format_ri
        }[self.format]

        freq_unit = {
            'Hz' : 1.,
            'kHZ' : 1e3,
            'MHZ' : 1e6,
            'GHZ' : 1e9
        }[self.freq_unit]

        for row in rows:
            freqs.append(row[0]*freq_unit)
            columns = row[1:]
            for i in range(len(self.names)):
                name = self.names[i]
                ports[name].append(formatter(columns[2*i], columns[2*i+1]))

        return freqs, ports

    def calculate_names(self):
        """Calculates the formal name for a given column
        """
        if self.n != 4:
            raise(NotImplementedError, "Only 4 port files are supported")
        if self.n == 4:
            for i in range(1,5):
                for j in range(1,5):
                    self.names.append(self.param + str(i) + str(j))


    @staticmethod
    def format_ma(mag, ang):
        return mag*np.e**(1j*ang*2*np.pi/360.)

    @staticmethod
    def format_db(db, ang):
        return (20**(db/20))*np.e**(1j*ang*2*np.pi/360.)

    @staticmethod
    def format_ri(real, img):
        return real + 1j*img


def db(value):
    return 20*np.log10(np.abs(value))

if __name__ == "__main__":
    import sys, os
    sys.path.append(r'P:\Code\Jplot')
    os.environ['QT_API'] = 'pyside'

    from jplot.qt_bindings import QtGui, QtCore, Qt, Signal
    from jwave import Wave
    from jplot import *
    from jplot.plot_window import PlotWidget


    s = Touchstone(r'P:\models\channel_models\peters_01_0904_B1_thru.s4p')

    s21 = Wave(x=s.freqs, y=s.ports['S21'],name="s21")

    impulse = s21.ifft()
    loss = db(s21(5e9).y[0])

    if False:
        from matplotlib import pyplot as plt
        fig, ax = plt.subplots()
        #plt.xscale('log')
        s21 = s.ports['S21']


        f = s.freqs
        ax.plot(f, 10*np.log10(np.abs(s21)), label="S21")
        ax.grid()

        ax.set_title('Insertion loss')
        plt.show()

    if True:
        app = QtGui.QApplication([])
        pw = PlotWidget("main")
        pw.plot(x=impulse.x, y=np.abs(impulse.y))
        pw.show()
        app.exec_()





