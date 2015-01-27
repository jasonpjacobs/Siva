from ..components import Component

class Analysis(Component):

    def start(self):
        self.init()
        for child in self.children:
            child.init()

    def init(self):
        """ The first step in a simulation.
        * Initialize local variables.
        * Creates local directories on the work disk.
        """
        for component in self.children:
            component.init()

    def reset(self):
        """
        Used to reset the component to the initial state after having been run.
        """
        for component in self.children:
            component.reset()

    def run(self):
        for component in self.children:
            component.run()

    def measure(self, results=None):
        for component in self.children:
            component.measure()

    def final(self):
        pass

    @property
    def editor(self):
        pass