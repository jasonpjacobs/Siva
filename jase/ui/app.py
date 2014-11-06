import logging
import sys, os
import glob
import jase

from PySide import QtCore, QtGui
from PySide.QtCore import Qt


class App(QtGui.QApplication):
    """
    """
    def __init__(self, name="Jase", version = jase.__version__):
        super().__init__(sys.argv)
        self.setApplicationName(name)
        self.setApplicationVersion(version)

        self.configureFont()

        # self.setWindowIcon()
        self.icons = {}
        self.load_icons()
        loger = logging.getLogger(name)
        logging.basicConfig(filename='jase.log',level=logging.DEBUG)
        loger.info("Starting JASE.")

    def configureFont(self):
        font = self.font()
        #font.setFamily('Verdana')
        font.setFamily('Arial')
        font.setPointSize(9)
        self.setFont(font)

    def load_icons(self):
        icons = glob.glob("../icons/*.png")
        pixmap = QtGui.QPixmap(100,100)
        pixmap.fill(QtGui.QColor("blue"))
        self.icons[''] = QtGui.QIcon(pixmap)
        for path in icons:
            dir, file_name = os.path.split(path)
            name = file_name.split('.')[0]
            self.icons[name] = QtGui.QIcon(path)


