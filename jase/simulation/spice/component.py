from ...components.component import Component as BaselineComponent


class Component(BaselineComponent):
    """An extension of the base Component class for Spice components.
    """

    def card(self):
        """Provides a text description of this component for Spice like netlists"""
        raise NotImplementedError("Subclases must define")


