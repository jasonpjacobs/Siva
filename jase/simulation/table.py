
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
        if hasattr(columns[0], 'keys'):
            values_dict = columns[0]
            for key in values_dict.keys():
                if key not in self.columns:
                    self.columns[key] = []
                self.columns[key].append(values_dict[key])

        else:
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
        num_rows = len(list(self.columns.values())[0])
        for row_num in range(num_rows):
            line = "  ".join(col_format.format(c[row_num]) for c in self.columns.values())
            lines.append(line)

        return "\n".join(lines)