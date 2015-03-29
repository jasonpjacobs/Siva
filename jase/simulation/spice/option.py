from ...components.directive import Directive
from ...components.parameter import String


class Option(Directive):
    registry_name = "options"

    def __init__(self, category=None, **kwargs):
        super().__init__()

        self.category = category
        self.options = kwargs
        self.name = 'option'

    def card(self):
        cards = []
        category = self.category if self.category is not None else ''
        for name, value in self.options.items():
            txt = ".OPTIONs {} {}={}".format(category, name, value)
            cards.append(txt)
        return [txt]
