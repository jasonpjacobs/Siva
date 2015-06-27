"""
Domains are general purpose terms to describe

* Clock domains
* Voltage (power) domain
* Reset domains

"""

from .design import Component

class Domain(Component):
    """ Base class for all subsequent domain Class definitions
    """

    def value(self):

class PowerDomain(Domain):
    """ A power domain is a collection of circuit that operate at the same voltage, and are
    enabled at the same time.
    """


class ClockDomain(Domain):
    """ A clock domain is a collection of circuits that operate at the same clock frequency,
    and are enabled at the same time.

    """