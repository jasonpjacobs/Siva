import pytest
import sys

from PySide import  QtCore, QtGui, QtTest
from jase.schematic.schematic import Schematic
from jase.ui.main import Main
from jase.ui.app import App
app = App()


if __name__ == "__main__":
    m = Main()
    m.setGeometry(100, 100, 1200, 800)
    m.show()

    m.status('Ready.')

    sys.exit(app.exec_())