from jase.components.directive import Directive

class Save(Directive):
    registry_name = "saves"

    token = ""
    def __init__(self, *items, type=None, analysis=None):

        super().__init__()

        self.items = items
        self.analysis = analysis
        self.type = type
        self.name = items[0].name
