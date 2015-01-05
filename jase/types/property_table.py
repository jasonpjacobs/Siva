# System Imports

# Third party imports
from ..qt_bindings import Qt, QtCore, QtGui

NAME_COLUMN = 0
VALUE_COLUMN = 1
#  =============================================
#        List Model
#  =============================================
class PropertyTable(QtCore.QAbstractTableModel):
    """
    Take a Type'd object and represents it's Type'd attributes
    in a Qt TableModel with name and value columns
    """

    def __init__(self,obj=None, parent=None, rows=None):
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self.obj = obj
        # If specific columns are not specified, use any Type'd attribute.
        if rows is None:
            self.rows = list(obj._descriptors.keys())
        else:
            self.rows = rows
        self.descriptors = obj._descriptors

    # ============================================================
    #            TableModelInterface
    # ============================================================
    def rowCount(self, parent=None):
        return len(self.rows)

    def columnCount(self, parent=None):
        return 2

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == NAME_COLUMN:
                return "Name"
            if section == VALUE_COLUMN:
                return "Value"
            return None
        # Row numbers
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return section + 1

    def data(self, index, role):
        row = index.row()
        column = index.column()
        attr = self.rows[row]
        descriptor = self.descriptors[attr]
        obj = self.obj

        # ---- Display (Text) Role ----
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if column == NAME_COLUMN:
                return descriptor.name
            elif column == VALUE_COLUMN:
                return str(getattr(self.obj, attr))
            else:
                return None

        # ---- ToolTip Role ----
        elif role == Qt.ToolTipRole:
            if descriptor.tool_tip is not None:
                return descriptor.tool_tip
            else:
                return descriptor.desc

        # ---- Font Role ----
        elif role == Qt.FontRole:
            if column == NAME_COLUMN:
                return None
            return descriptor.getFont(self.obj)

        # ---- Decoration (Icon) Role ----
        elif role == Qt.DecorationRole:
            if column == VALUE_COLUMN:
                return descriptor.getIcon(self.obj)
            else:
                return None

        # ---- CheckState (Checkbox) Role ----
        elif role == Qt.CheckStateRole:
            if column == VALUE_COLUMN and descriptor.checkbox is True:
                if descriptor.checkState(self.obj) is True:
                    return Qt.Checked
                else:
                    return Qt.Unchecked

        # ---- Size Hint Role (TODO: Use font metrics to determine size hint)
        elif role == Qt.SizeHintRole:
            return None

        # ---- Foreground (Font Color) Role ----
        elif role == Qt.ForegroundRole:
            if column == VALUE_COLUMN:
                return descriptor.getFontColor(obj)
            else:
                return None

        elif role == Qt.BackgroundRole:
            if column == NAME_COLUMN:
                return QtGui.QColor(240,240,240)
            if column == VALUE_COLUMN:
                return descriptor.getBGColor(obj)
        return None

    def setData( self, index,  value,  role):
        obj=self.obj
        attr = self.rows[index.row()]
        descriptor = self.descriptors[attr]
        assert descriptor is not None
        if role==Qt.EditRole and index.column()==VALUE_COLUMN:
            result = descriptor.setData(obj, value)
            return result
        if role==Qt.CheckStateRole:
            if descriptor.checkbox:
                if value == Qt.Checked:
                    descriptor.setData(obj, True)
                elif value == Qt.Unchecked:
                    descriptor.setData(obj, False)
            return True
        return False


    def flags(self, index):
        row = index.row()
        column = index.column()
        key = self.rows[row]
        descriptor = self.descriptors[key]
        if column == NAME_COLUMN:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        elif column == VALUE_COLUMN:
            flags = descriptor.flags(self.obj)
            return flags
        else:
            return Qt.ItemIsEnabled

    def getRow(self, n):
        return [v for v in self.descriptors.values()][n]



#  =============================================
#        List Widget
#  =============================================
class ListWidget(QtGui.QWidget):
    """ A QWidget to display and edit an object's attributes
    """
    def __init__(self, parent=None, model=None, title="Manifest", width=200, height=300, icons={}):
        super(ListWidget, self).__init__(parent=parent,)
        self.setWindowTitle(title)

        # The view
        self.view = QtGui.QTableView()
        if model is not None:
            self.view.setModel(model)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

        model = self.view.model()
        model.modelReset.connect(self.handleModelUpdate)

        self.handleModelUpdate()

    def setModel(self, model):
        self.view.setModel(model)
        self.modelReset.emit()

    def handleModelUpdate(self):
        self.setupDelegates()
        self.view.resizeRowsToContents()
        self.view.resizeColumnToContents(0)

    def setupDelegates(self):
        for row in range(self.view.model().rowCount()):
            descriptor = self.view.model().getRow(row)
            if descriptor.editor is not None:
                self.view.setItemDelegateForRow(row, descriptor.editor)

