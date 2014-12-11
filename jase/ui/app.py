import logging
import sys, os
import glob
import jase

from ..api import Qt, QtCore, QtGui


class App(QtGui.QApplication):
    """
    """
    current = None
    def __init__(self, name="Jase", version = jase.__version__):
        super().__init__(sys.argv)
        self.setApplicationName(name)
        self.setApplicationVersion(version)

        self.configureFont()
        self.setStyle('cleanlooks')
        # self.setWindowIcon()
        self.icons = {}
        self.load_icons()
        loger = logging.getLogger(name)
        logging.basicConfig(filename='jase.log',level=logging.DEBUG)
        loger.info("Starting JASE.")
        App.current = self

    def configureFont(self):
        font = self.font()
        #font.setFamily('Verdana')
        font.setFamily('Arial')
        font.setPointSize(9)
        self.setFont(font)

    def load_icons(self):
        icon_path = os.path.join(jase.__path__[0],'icons')
        icons = glob.glob(icon_path + "\*.png")
        pixmap = QtGui.QPixmap(100,100)
        pixmap.fill(QtGui.QColor("blue"))
        self.icons[''] = QtGui.QIcon(pixmap)
        for path in icons:
            dir, file_name = os.path.split(path)
            name = file_name.split('.')[0]
            self.icons[name] = QtGui.QIcon(path)


