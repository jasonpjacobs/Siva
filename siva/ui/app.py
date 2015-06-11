import logging
import sys, os
import glob
import siva

from ..qt_bindings import QtCore, QtGui, Qt
from ..icons import load_icons

class App(QtGui.QApplication):
    """
    """
    current = None
    def __init__(self, name="SiVA", version = siva.__version__):
        super().__init__(sys.argv)
        self.setApplicationName(name)
        self.setApplicationVersion(version)

        self.configureFont()
        self.setStyle('cleanlooks')
        # self.setWindowIcon()
        self.icons = {}
        self.load_icons()
        loger = logging.getLogger(name)
        logging.basicConfig(filename='siva.log',level=logging.DEBUG)
        loger.info("Starting SiVA.")
        App.current = self

    def configureFont(self):
        font = self.font()
        font.setFamily('Arial')
        font.setPointSize(9)
        self.setFont(font)

    def load_icons(self):
        self.icons = load_icons()


