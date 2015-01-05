import os
print("Chosing qt bindig")
if 'QT_API' in os.environ:
    qt_api = os.environ['QT_API']
else:
    qt_api = 'pyqt'

if qt_api == 'pyqt':
    try:
        from PyQt4 import QtCore, QtGui
        from PyQt4.QtCore import Qt
        from PyQt4.Qt import QTest
        os.environ['QT_API'] = 'pyqt'
    except ImportError:
        qt_api = 'pyside'

if qt_api == 'pyside':
    from PySide import QtCore, QtGui
    from PySide.QtCore import Qt
    from PySide.QtTest import QTest
    os.environ['QT_API'] = 'pyside'