import sys


from ..qt_bindings import Qt, QtCore, QtGui
from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager

import jase


class Console(RichIPythonWidget):
    def __init__(self, **kwarg):

        super(RichIPythonWidget, self).__init__()
        self.kernel_manager = QtInProcessKernelManager()
        self.kernel_manager.start_kernel()
        self.kernel = self.kernel_manager.kernel
        #self.kernel.shell.user_ns.update(kwargs)



        self.kernel.gui = 'qt4'
        self.kernel.shell.push(kwarg)
        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()


        policy = QtGui.QSizePolicy()
        policy.setHorizontalPolicy(QtGui.QSizePolicy.Minimum)
        policy.setVerticalPolicy(QtGui.QSizePolicy.Minimum)
        self.setSizePolicy(policy)

    def sizeHint(self, *args, **kwargs):
        return QtCore.QSize(100,600)

    def sizeHint(self):
        return QtCore.QSize(20,120)

    @property
    def banner(self):
        return '\n'.join([
            u"JASE v{}, \N{copyright sign} 2014, Juliet Design Automation".format(jase.__version__),
            "on Python {}".format(sys.version[:5])

        ])
