
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
        # Default printed column width.  Place holder for more explicit formatting
        # options that will be developed later
        self.w = 8

    def add_row(self, *columns, row=None):
        """Adds a row to the table to the specified row.  If the row is not
        specified, the row is added to the end of the table.

        The columns argument can be given as a dictionary of column/value pairs, or
        as a list of values.  If a list of values is given, the table's native column
        order is assumed.
        """

        # Handle columns as a dictionary
        if hasattr(columns[0], 'keys'):
            values_dict = columns[0]
            for key in values_dict.keys():
                # Create the column dict if it does not already exist.
                if key not in self.columns:
                    self.columns[key] = []
        # Handle a list of values
        else:
            values_list = columns
            if not len(columns) == len(self.columns):
                raise ValueError("Number of items does not match the number of columns. {} vs {}".format(
                    len(columns),len(self.columns)))
            values_dict = dict((k,v) for k,v in zip(self.columns.keys(), values_list))

        # Now handle the row argument.  If the row is None, append the data
        if row is None:
            for key in self.columns.keys():
                self.columns[key].append(values_dict[key])
        else:
            for key, col in self.columns.items():
                while len(col) < row + 1:
                    col.append(None)
                if key in values_dict:
                    col[row] = values_dict[key]



    def __str__(self):
        # Check for empty table
        if len(self.columns) == 0:
            return "<Empty Table>"

        lines = []
        w = self.w
        col_format = "{:" + str(w) + "}"

        # Header
        lines.append("  ".join(col_format.format(l).capitalize() for l in self.columns.keys()))

        # Separator
        lines.append("  ".join(col_format.format(w*"-").capitalize() for l in self.columns.keys()))

        # Rows
        for row_num in range(self.num_rows):
            line = "  ".join(col_format.format(c[row_num]) for c in self.columns.values())
            lines.append(line)

        return "\n".join(lines)

    @property
    def num_rows(self):
        if len(self.columns) == 0:
            return 0
        return max([len(col) for col in self.columns.values()])

    @property
    def is_empty(self):
        return self.num_rows == 0

    def __getitem__(self, item):
        return self.columns[item]

    def __len__(self):
        return self.num_rows

    def get_row(self, row):
        if row > len(self) - 1:
            raise IndexError("Table only has {} rows. Row {} requested.".format(len(self), row + 1))
        row_dict = OrderedDict()
        for column in self.columns:
            row_dict[column] = self.columns[column][row]
        return row_dict

    def __iter__(self):
        self._current_row = 0
        return self

    def __next__(self):
        if self._current_row > len(self) - 1:
            raise StopIteration

        row = self.get_row(self._current_row)
        self._current_row += 1
        return row




