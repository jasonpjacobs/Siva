"""A cell-based module that does no importing via __init__.py
"""

__version__ = "1.0.1"
__author__ = "Jase"


from .symbol import Symbol

__views__ = {}
__views__['symbol'] = Symbol
