import pytest
from ..api import Qt, QtCore, QtGui

from jase.ui.main import Main



@pytest.fixture
def app():
    if QtGui.QApplication.instance():
        app = QtGui.QApplication.instance()
        app.quit()

    app = QtGui.QApplication([])
    return app

def test_test(app):


    main = Main()
    main.show()

    #app.exec_()
