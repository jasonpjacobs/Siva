from PySide import QtCore, QtGui

from jtypes.table_model import TableModel, TableView

class DeviceCanvas(TableView):
    pass

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
        self.cellLabel = QtGui.QLabel("Cell Filter")
        self.cellEntry = QtGui.QLineEdit("*")
        self.viewLabel = QtGui.QLabel("Views")
        self.viewEntry = QtGui.QLineEdit("symbol footprint")
        self.collectionLabel = QtGui.QLabel("Collections")
        self.collectionEntry = QtGui.QLineEdit("*")

        self.deviceLabel = QtGui.QLabel("Devices")
        self.deviceCanvas = DeviceCanvas()

        # Configure the device canvas
        self.deviceCanvas.setIconSize(QtCore.QSize(100,100))
        self.deviceCanvas.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        #self.deviceCanvas.setView

        self.setGeometry(300, 300, 350, 250)

        grid = QtGui.QGridLayout()
        #grid.addWidget(self.collectionLabel, 0, 0)
        #grid.addWidget(self.collectionEntry, 0, 1)
        grid.addWidget(self.libLabel, 1, 0)
        grid.addWidget(self.libEntry, 1, 1)

        grid.addWidget(self.cellLabel, 2,0)
        grid.addWidget(self.cellEntry,2,1)

        #grid.addWidget(self.viewLabel, 3 ,0)
        #grid.addWidget(self.viewEntry,3,1)

        grid.addWidget(self.deviceLabel,4,0)
        grid.addWidget(self.deviceCanvas,5,0,9,2)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(grid)
        self.setLayout(layout)

        self.lib_defs = lib_defs
        if lib_defs:
            self.populateLib()

        # Signals/slots
        self.libEntry.currentIndexChanged.connect(self.onLibChange)

    def populateLib(self):
        for lib in self.lib_defs:
            self.libEntry.addItem(lib)
        model = TableModel(data=[], columns=['name'])
        self.deviceCanvas.setModel(model)
        self.onLibChange()

    def onLibChange(self):
        lib_name = str(self.libEntry.currentText())

        assert lib_name in self.lib_defs

        lib = self.lib_defs[lib_name]
        cell_names = [c for c in lib]
        cell_names.sort()
        print("New cells are", list(lib.values()))
        self.deviceCanvas.set_model_data(list(lib.values()))