
from collections import OrderedDict
class Table:
    """ Simple table structure implemented a table as a dict of lists.
    Used as a temporary storage for simulation data for conversion to
    pytables or h5py
    """
    def __init__(self, columns=None):
        self.columns = OrderedDict()
        if columns is not None:
            for col_name in columns:
                self.columns[col_name] = []

        # Default column width.  Place holder for more explicit formatting
        # options that will be developed later
        self.w = 8


    def add_row(self, *columns):
        if hasattr(columns, 'keys'):
            for key in columns:
                if key not in self.columns:
                    self.columns[key] = []
                self.columns[key].append(columns[key])

        # list
        if not len(columns) == len(self.columns):
            raise ValueError("Number of items does not match the number of columns. {} vs {}".format(
                len(columns),len(self.columns)))

        for val, col in zip(columns, self.columns.values()):
            col.append(val)

    def __str__(self):
        lines = []
        w = self.w
        col_format = "{:" + str(w) + "}"

        # Header
        lines.append("  ".join(col_format.format(l).capitalize() for l in self.columns.keys()))

        # Separator
        lines.append("  ".join(col_format.format(w*"-").capitalize() for l in self.columns.keys()))

        # Rows
        l = len(list(self.columns.values())[0])
        for i in range(len(self.columns)):
            line = "  ".join(col_format.format(l[i]) for l in self.columns.values())
            lines.append(line)

        return "\n".join(lines)