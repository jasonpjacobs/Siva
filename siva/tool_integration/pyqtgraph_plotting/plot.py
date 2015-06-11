""" A simple waveform plotter based on the Pyqtgraph Graphics Window
"""
import pyqtgraph as pg

class Plot(pg.GraphicsWindow):

    def __init__(self, title="Plot", size=(1200,800)):
        super().__init__(title=title, size=size)
        self.subplots = {}
        self.current_subplot = None

    def plot(self, x, y, color=None, name=None, subplot=None, x_scale='linear', y_scale='linear'):
        if subplot is None:
            plot = self.current_subplot
        else:
            plot = self.subplots.get(name, None)

        if plot is None:
            n = len(self.subplots)
            if name is None:
                name = "Plot:" + str(n)

            plot = self.addPlot(0,n, title=subplot)
            plot.showGrid(True, True)
            plot.setLogMode( x_scale=='log', y_scale=='log')
            plot.addLegend()

            self.current_subplot = plot

        plot.plot(x, y, pen=color, name=name)
