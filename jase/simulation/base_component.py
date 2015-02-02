from ..components import Component

class BaseComponent(Component):
    """ Base class for all simulation components

    This class defines how each component is executed.
    """
    def start(self):
        self._init()
        self._execute()
        self._final()

    def _init(self):
        """ The first step in a simulation.
        * Initialize local variables.
        * Creates local directories on the work disk.
        """
        self.init()
        for component in self.children.values():
            component._init()

    def _reset(self):
        """
        Used to reset the component to the initial state after having been run.
        """
        self.reset()
        for component in self.children.values():
            component._reset()

    def _execute(self):
        """ Execute the component's main task.  Simulation components will run the simulation. Loop components
        will increment and set loop variables.  Search components will start a new set of trials.
        """
        self.execute()
        for component in self.children.values():
            component._execute()
        self.measure()

    def _measure(self):
        for component in self.children.values():
            component._measure()
        self.measure()

    def _final(self):
        for component in self.children.values():
            component._final()
        self.final()

    def init(self):
        """ The first step in a simulation.
        * Initialize local variables.
        * Creates local directories on the work disk.
        """
        pass

    def reset(self):
        """
        Used to reset the component to the initial state after having been run.
        """
        pass

    def execute(self):
        pass

    def measure(self, results=None):
        pass

    def final(self):
        pass

    def init(self):
        """ The first step in a simulation.
        * Initialize local variables.
        * Creates local directories on the work disk.
        """
        pass

    @property
    def editor(self):
        pass


