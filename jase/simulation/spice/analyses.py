from ..analysis import Analysis
from ..variable import Variable, Float

class Tran(Analysis):
    analysis_name = "tran"
    step = Float()
    stop = Float()

