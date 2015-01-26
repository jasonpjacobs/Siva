from ..components import Component

class Analysis(Component):

    def init(self):
        """ The first step in a simulation.
        * Initialize local variables.
        * Creates local directories on the work disk.
        """
        for component in self._components:
            component.init()

    def reset(self):
        """
        Used to reset the component to the initial state after having been run.
        """
        for component in self._components:
            component.reset()

    def run(self):
        for component in self._components:
            component.run()

    def post_process(self, results=None):
        for component in self._components:
            component.post_process()

    def clean_up(self):
        pass


    def start(self):
        self.init()
        for child in self.children:
            child.init()

        

    @property
    def editor(self):
        pass