import pytest
__author__ = 'Jase'

import unittest
from siva.plotting.plot_view import PlotView
from siva.plotting.plot import Plot
from siva.plotting.scale import Scale
from siva.qt_bindings import QtGui

from ..plot import Plot, PlotGroup

import sys
import numpy as np
import pdb

try:
    app = QtGui.QApplication([])
except:
    app = QtGui.QApplication.instance()



def test_child_bounding_rect():
    pv = PlotView(height=800)
    rect = QtGui.QGraphicsRectItem(100,100, 200,200)
    pv.scene.addItem(rect)

    br = rect.boundingRect()
    assert br is not None

    assert br.left() == 100
    assert br.top() == 100

    group = QtGui.QGraphicsItemGroup()
    group.setPos(100,100)
    group.addToGroup(rect)

    br = group.boundingRect()
    assert br is not None

    assert br.left() == 0
    assert br.top() == 0

    assert

    pv.show()
    sys.exit(app.exec_())



