from PySide import QtGui, QtCore

class PropertiesWidget(QtGui.QTableWidget):

    def __init__(self):
        super().__init__()
        policy = QtGui.QSizePolicy()
        policy.setHorizontalPolicy(QtGui.QSizePolicy.Minimum)
        policy.setVerticalPolicy(QtGui.QSizePolicy.Expanding)
        self.setSizePolicy(policy)

    def sizeHint(self, *args, **kwargs):
        return QtCore.QSize(100,200)