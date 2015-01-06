import pytest
from ..qt_bindings import QtCore, QtGui, QTest

from jase.ui.app import App
from jase.ui.main import Main



@pytest.fixture
def app():
    if QtGui.QApplication.instance():
        app = QtGui.QApplication.instance()
        app.quit()

    app = App()
    return app

def test_test():

    app = App()
    main = Main(app=app)
    main.show()

    #app.exec_()
