import pytest
import os
import numpy as np

os.environ['QT_API'] = 'pyside'
print(os.environ['QT_API'])


from ...qt_bindings import QtGui, QtCore, QTest, Qt
from ..plot import Plot
from ..plot_group import PlotGroup
from ..plot_view import PlotView
from ..plot_items import LinePlot, LogicPlot, BarPlot, StemPlot, StatePlot
from ..scale import Scale

INTERACTIVE = True

if QtGui.QApplication.instance():
    app = QtGui.QApplication.instance()
else:
    app = QtGui.QApplication([])



class TestWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.scene=QtGui.QGraphicsScene(self)
        self.view = QtGui.QGraphicsView(self.scene, self)
        self.x_scale = Scale(plot=self, axis="x")
        self.y_scale = Scale(plot=self, axis="y")

        self.setGeometry(100,100, 500, 200)

        #self.layout = QtGui.QVBoxLayout()
        #self.layout.addItem(self.view)
        self.view.setAlignment(Qt.AlignCenter)
        self.view.setTransformationAnchor(QtGui.QGraphicsView.NoAnchor)
        self.view.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        self.view.setMouseTracking(True)


    def add_plot(self, plot):
        self.scene.addItem(plot)
        #plot.setParentItem(self)

@pytest.fixture
def widget():
    w = TestWidget()
    return w


@pytest.mark.skipif(False, reason="Debugging other tests")
def test_plot(widget):

    #view = widget.view

    view = PlotView()
    N=20
    view.plot(x=np.arange(N), y=np.random.random(N), line_color='blue')
    view.plot(x=np.arange(N), y=np.random.random(N), line_color='red')

    if INTERACTIVE:
        view.show()
        app.exec_()

    assert True


@pytest.mark.skipif(True, reason="Debugging other tests")
def test_line_plot(widget):
    N=100
    x=np.arange(N)
    y=np.random.random(N)*10

    plot = Plot()
    plot.plot(x=x, y=y)
    plot.zoom_fit()
    line = LinePlot(x=x, y=y, plot=plot)

    r = plot.boundingRect()
    assert r.width() == 400
    assert r.height() == 100


    if INTERACTIVE:
        widget.add_plot(plot)
        widget.show()
        app.exec_()

