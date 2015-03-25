# System imports
from collections import OrderedDict
import pdb

# Third party imports
from jase.qt_bindings import Qt, QtCore, QtGui

class ListModel(QtCore.QAbstractListModel):
    def __init__(self, data=None, descriptors=None, columns=None, path=None):
        super().__init__(parent=None)

        if data is not None:
            self.model_data = data
        else:
            self.model_data = []

        self.path = path
        self.columns = columns

        if descriptors is None:
            self.descriptors = OrderedDict()
            if data is not None:
                for item in data:
                    dct = getattr(item, '_descriptors', None)
                    pdb.set_trace()
                    if dct:
                        self.descriptors.update(dct)
        else:
            self.descriptors = descriptors

        # 'columns' is a list of attributes to display.  If None, displays all of them.
        if columns is None:
            columns = [k for k in self.descriptors.keys()]

        self.setSupportedDragActions(Qt.CopyAction | Qt.LinkAction | Qt.MoveAction)

    # Helper methods

    def set_model_data(self, data, columns=None):
        self.model_data = data
        if columns is not None:
            self.columns = columns
        self.find_descriprors()
        self.reset()

    def find_descriprors(self):
        data = self.model_data
        if data is not None:
            for item in data:
                dct = getattr(item, '_descriptors', None)
                if dct:
                    self.descriptors.update(item._descriptors)

    def get_descriptor(self, index):
        'Helper function to return the descriptor associated with this column.  Used in most of the TableModel interface'
        column = index.column()
        column_name = self.columns[column]
        descriptor = self.descriptors.get(column_name)
        return descriptor

    def get_row(self, row):
        """Retrieves an object from the model by row index"""
        if row < len(self.model_data):
            return self.model_data[row]
        return None

    def get_obj_name(self, row):
        """Returns the object name from the model by row index"""
        return [k for k in self.model_data.keys()][row]

    def get_attr(self, index):
        descriptor = self.get_descriptor(index)
        return descriptor.attr

    # ================================================================
    # TableModel Interface - View Methods
    # ================================================================
    def data(self, index, role):
        descriptor = self.get_descriptor(index)
        if descriptor is None:
            return None

        row = index.row()
        column = index.column()
        obj = self.get_row(row)

        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            data = descriptor.data(obj)
            return descriptor.data(obj)

        if role == Qt.EditRole:
            return descriptor.data(obj)

        if role == Qt.UserRole:
            return None

        if role == Qt.ToolTipRole:
            return descriptor.tool_tip

        if role == Qt.DecorationRole:
            if row < self.rowCount():
                return descriptor.getIcon(obj)

        if role == Qt.FontRole:
            return descriptor.getFont(obj)

        if role == Qt.ForegroundRole:
            if row == self.rowCount() - 1:
                return None
            return descriptor.getFontColor(obj)

        if role == Qt.BackgroundRole:
            return descriptor.getBGColor(obj)

        if role == Qt.CheckStateRole:
            if obj is None:
                return None
            if not descriptor.checkbox:
                return None
            return descriptor.checkState(obj)
        return None

    def hasChildren(self, parent):
        return len(self.model_data) > 0

    def parent(self, index):
        """
        """
        # List models have no parent
        return QtCore.QModelIndex()

    def index(self, row, column, parent):
        if row in range(len(self.model_data)) and column in range(len(self.columns)):
            return self.createIndex(row, column, None)
        else:
            return QtCore.QModelIndex()

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                name = self.columns[section]
                descriptor = self.descriptors[name]
                name = descriptor.name
                name = name.title().replace('_', ' ')
                return name

            if orientation == Qt.Vertical:
                return section

        # Display the descriptors 'desc' attribute as a tool tip
        if role == Qt.ToolTipRole:
            try:
                name = self.columns[section]
                descriptor = self.model_data[0].descriptors[name]
                if descriptor.desc is not None:
                    return QtCore.QString(descriptor.desc)
            except:
                raise
        # Default action
        return None

    def rowCount(self, parent=QtCore.QModelIndex()):
        """ Returns the number of rows under the given parent. When the parent is valid it means that rowCount is
        returning the number of children of parent.

        Note:  When implementing a table based model, PySide.QtCore.QAbstractItemModel.rowCount() should
        return 0 when the parent is valid.

        (From the QAbstractTableModel documentation)

        Table models rows don't have a parent, so the empty parent index should always be used
        to access rows
        """
        if parent.isValid():
            return 0

        # Top level items should have an invalid parent index.
        return len(self.model_data)

    def columnCount(self, parent):
        return len(self.columns)

    # ================================================================
    # TableModel Interface - Edit Methods
    # ================================================================
    def flags(self, index):
        if not index.isValid():
            return 0
        row = index.row()
        column = index.column()
        descriptor = self.get_descriptor(index)
        if descriptor is not None:
            obj = self.get_row(index.row())
            flags = descriptor.flags(obj)
            return flags
        return Qt.NoItemFlags

class ListView(QtGui.QListView):
    def __init__(self, data=None, descriptors=None, model=None, parent=None, path='', columns=None):
        super().__init__(parent=None)
        self.setModel(model)
        #self.setStyleSheet("background: qlineargradient(spread:pad, x1:0, y1:0, x2:.25, y2:1, stop:1 rgba(200, 200, 200, 255), stop:0 rgba(210, 210, 210, 210))")

        if model is not None:
            pass
        elif data is None:
            if model is None:
                model=ListModel(data=[], descriptors=None, path=path, columns=columns)
            else:
                model=ListModel(data=data, descriptors=descriptors, path=path, columns=columns)
        else:
            model=ListModel(data=data, descriptors=descriptors, path=path, columns=columns)

        model.modelReset.connect(self.on_model_reset)

        if model is not None:
            self.setModel(model)
            self.on_model_reset()

        # Drag and Drop
        self.setDragEnabled(True)

    def set_model_data(self, data, columns=None):
        model = self.model()
        model.set_model_data(data, columns)

    def on_model_reset(self):
        self.findDelegates()

    def findDelegates(self):
        # Look at the descriptors used with the model
        # and if the have an editor (delegate) specified
        # set the view to use it.
        column_names = [c for c in self.model().columns]
        for i in range(len(column_names)):
            attr_name = column_names[i]
            descriptor = self.model().descriptors.get(attr_name)

            if descriptor is not None and descriptor.editor is not None:
                self.setItemDelegateForColumn(i, descriptor.editor)
