from ..qt_bindings import QtGui, QtCore, Qt
from ..types.table_model import TableModel, TableView

from siva.types.list_model import ListModel, ListView
from siva.types.types import Typed, Str

from ..views.symbol import Symbol

class NameType(Str):
    def getIcon(self, obj):
        return obj.icon

    def flags(self, obj):
        flags = super().flags(obj)
        flags |= Qt.ItemIsDragEnabled
        return flags

class CellProxy(Typed):
    name = NameType()

    def __init__(self, name, icon):
        self.name = name
        self.icon = icon

    def getIcon(self, name, obj):
        print("Getting icon from", obj, obj.icon)
        return obj.icon

class DeviceCanvas(ListView):
        def __init__(self, data=None):
            super().__init__(columns=['name'], descriptors=CellProxy._descriptors)

class DeviceSelectorWidget(QtGui.QWidget):
    symbol_types = (Symbol,)
    '''
    classdocs
    '''
    def __init__(self, libraries=None):
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
        self.deviceCanvas.setIconSize(QtCore.QSize(30,30))
        self.deviceCanvas.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.deviceCanvas.setViewMode(QtGui.QListView.ListMode)
        self.deviceCanvas.setMovement(QtGui.QListView.Static)

        #self.deviceCanvas.setFlow(QtGui.QListView.TopToBottom)
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

        self.libraries = libraries
        if libraries:
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
        lib_names = [k for k in self.libraries.keys()]
        for lib_name in sorted(lib_names):
            self.libEntry.addItem(lib_name)
        self.onLibChange()

    def onLibChange(self):
        lib_name = str(self.libEntry.currentText())
        assert lib_name in self.libraries
        lib = self.libraries[lib_name]

        values = []
        for cell_name in lib:
            cell = lib[cell_name]
            for view in cell.__views__.values():
                if issubclass(view, self.symbol_types):
                    values.append(CellProxy(name=cell.name, icon=cell.icon))
        self.deviceCanvas.set_model_data(values)

