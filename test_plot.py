import os
os.environ['QT_API'] = 'pyside'

from jase.plotting.plot_window import PlotWidget
from jase.plotting.plot import Plot
from jase.plotting.scale import Scale
from jase.qt_bindings import QtGui
import sys
import numpy as np
import pdb

try:
    app = QtGui.QApplication([])
except:
    app = QtGui.QApplication.instance()

pw = PlotWidget(name="main")
pw.setGeometry(100,100, 1000, 800)

if False:
    p = Plot()
    scale = Scale(plot=p)

    for i in range(100):
        scale.scale = np.random.random()
        scale.offset = np.random.random()
        for s in np.arange(-10, 10, 0.5):
            d = scale.to_data(s)
            s1 = scale.to_screen(d)
            if not s - s1 < 1e-12:
                print("{}<->{}  {}".format(s, s1, d))

    sys.exit()

def test_random():
    #plot = Plot(w=800, h=400, title="Simple waveforms")
    #plot.plot(x=[0,20], y=[0,0])
    #plot.plot(x=[0,2], y=[0,1], style="line")

    #plot.plot(x=[0,20], y=[20,20])
    y = 10*np.random.random(200)
    #plot.plot(x=np.arange(200)/10,y=y, style="line")
    #plot.plot(x=np.arange(200)/10,y=y, style="line")

def test_multiple_plots():

    if True:
        pw.plot(x=[0,10], y=[0, 0], strip="Wave", name="1", color="red", height=20)

    if True:
        pw.plot(x=[0,10], y=[0, 1], strip="Wave", name="2", color="green")
        pw.plot(x=[0,10], y=[-12, 5], strip="Wave", name="3", color="blue")
        pw.plot(x=[0,10], y=[0, 0], strip="Wave", name="4", color="yellow")


    if True:
        states = ["Unknown", "Reset", "Idle", "Active", "Gen1"]
        pw.plot(x=[0,1,4,5,10], y=states, style="state", name="state_plot", strip="Wave")
        pw.plot(x=[0,4,15,20, 21], y=states, style="state", name="state_plot2", strip="Wave")


    if True:
        x = np.linspace(0, 20, 100)
        f=1/10.
        y = 2*np.sin(2*np.pi*f*x) + 7
        pw.plot(x=x, y=y, style="line", strip="Wave", name="sin")
        pw.plot(x=x, y=np.sin(2*np.pi*5*f*x), style="line", strip="Wave", name="sin")
        pw.plot(x=x, y=1/(x+1), style="line", strip="Wave", name="sin")
        pw.plot(x=x, y=x**2, style="line", strip="Wave", name="sin")

    if True:
        for i in range(0):
            x = np.arange(10) + .1*np.random.random(10)
            y = np.round(np.random.random(len(x)))
            pw.plot(x=x,y=y, style="logic", n=i+1, strip="Wave2", name="")
    if True:
        pw.plot(x=[0,10], y=[0, 0], strip="Wave", name="db", color="red")


def test_small_scales():
        x = np.linspace(0, 10e-9, 1000)
        f=4e12
        y = 2*np.sin(2*np.pi*f*x) + 7
        pw.plot(x=x, y=y, style="line", strip="Wave", name="sin")
        pw.plot(x=x, y=np.sin(2*np.pi*5*f*x), style="line", strip="Wave", name="sin")

def test_single_plot():
        x = np.arange(10)
        f=4e12
        y = np.random.random(10)
        pw.plot(x=x, y=y, style="line", strip="Wave", name="sin")
        pw.plot(x=x, y=y, style="line", strip="Wave", name="sin")


#multiple_plots()

#test_small_scales()
#test_multiple_plots()
#test_single_plot()
test_empty_plot()
pw.show()
sys.exit(app.exec_())