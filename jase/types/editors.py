# Python Imports
import sys, os, pdb
from pdb import set_trace as db

# Third party imports
from ...qt_bindings import QtCore, QtGui, Qt


# ================================================================
#    Combo Box
# ================================================================ 
class ComboBox(QtGui.QStyledItemDelegate):
    
    def __init__(self, values, *args):
        super(ComboBox, self).__init__(*args)
        self.values = values

    def createEditor(self, parent, option, index):
        "Returns the widget used to edit the item specified by index for editing. The parent widget and style option are used to control how the editor widget appears."
        editor = QtGui.QComboBox(parent)
        editor.addItems(self.values)
        return editor
    
    def setEditorData(self, editor, index):
        "Sets the data to be displayed and edited by the editor from the data model item specified by the model index."
        value = str(index.model().data(index, Qt.EditRole))
        editor.setEditText(value)
    
    def setModelData(self, editor, model, index):
        "Gets data from the editor widget and stores it in the specified model at the item index."
        value = editor.currentText()
        model.setData(index, value, Qt.EditRole)
        
    def updateEditorGeometry(self, editor, option, index):
        "Updates the editor for the item specified by index according to the style option given."
        editor.setGeometry(option.rect);
    """    
    def sizeHint(self, option, index):
        "Returns the size needed by the delegate to display the item specified by index, taking into account the style information provided by option."
    """

# ================================================================
#    Spin Box
# ================================================================ 
class SpinBox(QtGui.QStyledItemDelegate):
    
    def __init__(self, min=None, max=None, *args):
        super(SpinBox, self).__init__(*args)
        self.min = min
        self.max = max
        
    def createEditor(self, parent, option, index):
        "Returns the widget used to edit the item specified by index for editing. The parent widget and style option are used to control how the editor widget appears."
        editor = QtGui.QSpinBox(parent)
        
        if self.min is not None:
            editor.setMinimum(self.min)
        if self.max is not None:
            editor.setMaximum(self.max)    
        
        return editor
    
    def setEditorData(self, editor, index):
        "Sets the data to be displayed and edited by the editor from the data model item specified by the model index."
        value = int(index.model().data(index, Qt.EditRole))
        editor.setValue(value)
    
    def setModelData(self, editor, model, index):
        "Gets data from the editor widget and stores it in the specified model at the item index."
        value = editor.value()
        model.setData(index, value, Qt.EditRole)
        

    def updateEditorGeometry(self, editor, option, index):
        "Updates the editor for the item specified by index according to the style option given."
        editor.setGeometry(option.rect);
    """    
    def sizeHint(self, option, index):
        "Returns the size needed by the delegate to display the item specified by index, taking into account the style information provided by option."
    """



#class ComboBoxDelegate():
if __name__ == "__main__":
    app = QtGui.QApplication([])
    
    app.exec_()