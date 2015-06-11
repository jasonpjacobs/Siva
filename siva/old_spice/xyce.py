import struct
import pdb

import numpy as np

from siva.old_spice.spice import Spice


class Xyce(Spice):
    _parse_params = False
    simulator_path = "P:\\Tools\\Xyce\\bin\\Xyce.exe"

    def load_results(self, format="binary"):
        if format == "binary":
            bytes_read = open(self.results_file, "rb").read()

            marker = bytes('Binary:\n', "utf-8")
            start = bytes_read.find(marker) + len(marker)
            header = str(bytes_read[:start])
            lines = header.split("\\n")
            data = bytes_read[start:]

            size = len(data)/len(struct.pack('d',0.0))
            format = "{}d".format(int(size))

            # Parse the header to get wave names, number of vars and points
            headers = {}
            VARS_FOUND = False
            data_format = None
            for line in lines:
                if line == "Binary:":
                    break
                elif "No. Variables:" in line:
                    num_vars = int(line.split(":")[1])
                elif "No. Points:" in line:
                    try:
                        num_points = int([l for l in lines if "No. Points" in l][0].split(":")[1])
                    except ValueError:
                        # XYCE doesn't always fill in this field
                        num_points = None
                elif "Flags:" in line:
                    data_format = line.split(":")[1].strip()
                elif line == "Variables:":
                    VARS_FOUND = True
                    continue
                elif VARS_FOUND:
                    txt = line.replace("\\t", " ")
                    n, name, sig_type = txt.split()
                    headers[int(n)] = (int(n), name, sig_type)
                else:
                    continue

            if data_format == "real":
                cols_per_value = 1
            elif data_format == "complex":
                cols_per_value = 2
            else:
                print("ERROR:  XYCE results file wasn't formatted properly")
                pdb.set_trace()

            try:
                array = np.array(struct.unpack(format, bytes(data)))
            except:
                pdb.set_trace()


            if num_points is None:
                num_points = int(len(array)/(num_vars*cols_per_value))

            data = array.reshape((num_points, num_vars*cols_per_value))
            results = {}
            for n in headers:
                n, name, sig_type = headers[n]
                if data_format == "real":
                    results[name] = data[:,n]
                else:
                    results[name] = data[:,2*n] + data[:,2*n+1]*1j
            return results

