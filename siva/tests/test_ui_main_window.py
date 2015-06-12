import pytest
import os
from siva.qt_bindings import QtCore, QtGui, QTest

from siva.ui.app import App
from siva.ui.main import Main

import tempfile
work_dir = tempfile.mkdtemp()
os.chdir(work_dir)


@pytest.fixture
def app():
    if QtGui.QApplication.instance():
        app = QtGui.QApplication.instance()
        app.quit()

    app = App()
    return app


@pytest.mark.skipif(True, reason="Only works interactively.")
def test_test():
    app = App()
    main = Main(app=app)
    main.show()

    app.exec_()
