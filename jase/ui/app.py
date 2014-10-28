import logging
import sys, os
import glob

from PySide import QtCore, QtGui
from PySide.QtCore import Qt


class App(QtGui.QApplication):
    """
    """
    def __init__(self, name="Jase", version = "0.1"):
        super().__init__(sys.argv)
        self.setApplicationName(name)
        self.setApplicationVersion('0.1 - Beta')

        # self.setWindowIcon()
        self.icons = {}
        self.load_icons()
        loger = logging.getLogger(name)
        logging.basicConfig(filename='jase.log',level=logging.DEBUG)
        loger.info("Starting JASE.")

    def load_icons(self):
        icons = glob.glob("../icons/*.png")
        pixmap = QtGui.QPixmap(100,100)
        pixmap.fill(QtGui.QColor("blue"))
        self.icons[''] = QtGui.QIcon(pixmap)
        for path in icons:
            dir, file_name = os.path.split(path)
            name = file_name.split('.')[0]
            self.icons[name] = QtGui.QIcon(path)


