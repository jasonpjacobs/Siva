from ..components import Component

class AnalysisComponent(Component):

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

    def run(self):
        pass

    def post_process(self, results=None):
        pass

    def clean_up(self):
        pass

    @property
    def editor(self):
        pass