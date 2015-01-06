from ..qt_bindings import QtGui, QtCore, Qt

from .plot_view import PlotView
from collections import OrderedDict
import pdb

class PlotWidget(QtGui.QWidget):
    """ A Plot Widget that can hold multiple PlotViews in a grid.
    """
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name

        self.subwindows = OrderedDict()
        self.layout = QtGui.QGridLayout()

        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.MinimumExpanding)
        self.current_subwindow = None

        self.setGeometry(100, 100, 1200, 800)

    def subwindow(self, name, *args):
        if name in self.subwindows:
            subwindow = self.subwindows[name]
        else:
            subwindow = PlotView(width=self.width(), height=self.height())
            self.subwindows[name] = subwindow
            self.current_subwindow = subwindow
            self.layout.addWidget(subwindow, *args)
        return subwindow

    def plot(self, *args, subwindow=None, strip=None, **kwargs):
        if subwindow is None:
            if self.current_subwindow is None:
                name = "Plot Window"
                self.current_subwindow = self.subwindow(name=name)
            subwindow = self.current_subwindow
        elif subwindow in self.subwindows:
            subwindow = self.subwindows[subwindow]
        else:
            subwindow = self.subwindow(name=subwindow)
        subwindow.plot(strip=strip, *args, **kwargs)




