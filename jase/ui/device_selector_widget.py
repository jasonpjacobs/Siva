from PySide import QtCore, QtGui

from jtypes.list_model import ListModel, ListView

class DeviceCanvas(ListView):
    def __init__(self, data=None):
        super().__init__(columns=['name'])

class DeviceSelectorWidget(QtGui.QWidget):
    '''
    classdocs
    '''
    def __init__(self, lib_defs=None):
        '''
        Constructor
        '''
        super().__init__()

        self.libLabel = QtGui.QLabel("Library")
        self.libEntry = QtGui.QComboBox()
        self.libEntry.setEditable(True)
        self.cellLabel = QtGui.QLabel("Cell Filter")
        self.cellEntry = QtGui.QLineEdit("*")
        self.viewLabel = QtGui.QLabel("Views")
        self.viewEntry = QtGui.QLineEdit("symbol footprint")
        self.collectionLabel = QtGui.QLabel("Collections")
        self.collectionEntry = QtGui.QLineEdit("*")

        self.deviceLabel = QtGui.QLabel("Cells")
        self.deviceCanvas = DeviceCanvas()

        # Configure the device canvas
        self.deviceCanvas.setIconSize(QtCore.QSize(100,100))
        self.deviceCanvas.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        #self.deviceCanvas.setViewMode(QtGui.QListView.IconMode)

        #self.setGeometry(300, 300, 350, 250)

        grid = QtGui.QGridLayout()
        grid.addWidget(self.libLabel, 0, 0)
        grid.addWidget(self.libEntry, 0, 1)

        grid.addWidget(self.cellLabel, 1,0)
        grid.addWidget(self.cellEntry,1,1)

        grid.addWidget(self.deviceLabel,2,0)
        grid.addWidget(self.deviceCanvas,3,0,9,2)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(grid)
        self.setLayout(layout)

        self.lib_defs = lib_defs
        if lib_defs:
            self.populateLib()

        # Signals/slots
        self.libEntry.currentIndexChanged.connect(self.onLibChange)

        policy = QtGui.QSizePolicy()
        policy.setHorizontalPolicy(QtGui.QSizePolicy.Minimum)
        policy.setVerticalPolicy(QtGui.QSizePolicy.Expanding)
        self.setSizePolicy(policy)

    def sizeHint(self, *args, **kwargs):
        return QtCore.QSize(10,600)

    def populateLib(self):
        for lib in self.lib_defs:
            self.libEntry.addItem(lib)
        model = ListModel(data=[], columns=['name'])
        self.deviceCanvas.setModel(model)
        self.onLibChange()

    def onLibChange(self):
        lib_name = str(self.libEntry.currentText())
        assert lib_name in self.lib_defs
        lib = self.lib_defs[lib_name]
        self.deviceCanvas.set_model_data(list(lib.values()))

