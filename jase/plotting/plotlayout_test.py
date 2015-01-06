
import sys
from ..qt_bindings import QtGui, QtCore, Qt
import pdb

class Plot(QtGui.QGraphicsWidget):
    def __init__(self, *args, **kwargs):
        QtGui.QGraphicsWidget .__init__(self)
        #QtGui.QGraphicsRectItem.__init__(self, *args, **kwargs)

        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding, )
        return

    def sizeHint(self, *args, **kwargs):
        return QtCore.QSizeF(400, 100)

    def paint(self, painter, option, widget):
        print("Getting painted")
        painter.drawRect(self.boundingRect())
        print(self.pos())
        pass




class PlotGroup(QtGui.QGraphicsWidget):

    def __init__(self, parent):
        super().__init__(parent=parent)

        layout = QtGui.QGraphicsLinearLayout(Qt.Vertical, self)
        self.setLayout(layout)

        layout.addItem(Plot(0., 0., 500., 400.))
        layout.addItem(Plot(0., 0., 500., 200.))
        layout.addItem(Plot(0., 0., 500., 200.))
        layout.addItem(Plot(0., 0., 500., 200.))
        layout.addItem(Plot(0., 0., 500., 200.))



class Main(QtGui.QMainWindow ):

    def __init__(self):
        super().__init__()
        self.scene = QtGui.QGraphicsScene()
        view = QtGui.QGraphicsView()

        view.setScene(self.scene)
        self.setCentralWidget(view)

        top = PlotGroup(parent=None)
        self.scene.addItem(top)
        self.scene.setSceneRect(-100, -100, 800, 800)


        self.setWindowTitle('Main')
        self.setGeometry(100, 100, 400, 800)

        self.scene.addItem(QtGui.QGraphicsRectItem(QtCore.QRectF(100,100,10,10)))

    def resizeEvent(self, *args, **kwargs):
        super().resizeEvent(*args, **kwargs)
        #pdb.set_trace()


if __name__ == "__main__":

    app = QtGui.QApplication([])
    main = Main()
    main.show()
    sys.exit(app.exec_())