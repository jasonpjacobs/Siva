from .component import Component


class SimulationStatus:
    name = "Status"

    def __str__(self):
        return self.__class__.__name__

class Waiting(SimulationStatus):
    def __init__(self, resource=None):
        self.name = "Waiting"
        self.resource = resource

    def __str__(self):
        return "{}({})".format(self.name, str(self.resource))

class Running(SimulationStatus):
    name = "Running"
    def __init__(self, progress):
        self.name = "Running"
        self.progress = progress

    def __str__(self):
        return "{}({})".format(self.name, str(self.resource))

class Complete(SimulationStatus):
    name = "Complete"

class Simulation(Component):
    """ Generic simulation component
    """

    @property
    def status(self):
        return


