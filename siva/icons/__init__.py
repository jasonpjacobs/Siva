

__all__ = []

ICONS = {}

def load_icons():
    global ICONS

    import os
    import glob
    from ..qt_bindings import QtGui, QtCore

    icons = glob.glob(os.path.join(__path__[0], "*.png"))
    pixmap = QtGui.QPixmap(100,100)
    pixmap.fill(QtGui.QColor("blue"))
    ICONS[''] = QtGui.QIcon(pixmap)
    for path in icons:
        dir, file_name = os.path.split(path)
        name = file_name.split('.')[0]
        ICONS[name] = QtGui.QIcon(path)

    return ICONS