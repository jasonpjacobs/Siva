import psutil

"""

import builtins, io
openfiles = set()

oldfile = io.TextIOWrapper
#oldfile = builtins.file

class newfile(oldfile):
    def __init__(self, *args, **kwargs):
        self.x = args[0]
        print("### OPENING %s ###" % str(self.x))
        oldfile.__init__(self, *args, **kwargs)
        openfiles.add(self)

    def close(self):
        print("### CLOSING %s ###" % str(self.x))
        oldfile.close(self)
        openfiles.remove(self)

oldopen = builtins.open
def newopen(*args, **kwargs):
    return newfile(*args, **kwargs)
builtins.file = newfile
builtins.open = newopen

def printOpenFiles():
    print("### %d OPEN FILES: [%s]" % (len(openfiles), ", ".join(f.x for f in openfiles)))
"""

import os
import stat

_fd_types = (
    ('REG', stat.S_ISREG),
    ('FIFO', stat.S_ISFIFO),
    ('DIR', stat.S_ISDIR),
    ('CHR', stat.S_ISCHR),
    ('BLK', stat.S_ISBLK),
    ('LNK', stat.S_ISLNK),
    ('SOCK', stat.S_ISSOCK)
)


def fd_table_status():
    _fd_types = (
    ('REG', stat.S_ISREG),
    ('FIFO', stat.S_ISFIFO),
    ('DIR', stat.S_ISDIR),
    ('CHR', stat.S_ISCHR),
    ('BLK', stat.S_ISBLK),
    ('LNK', stat.S_ISLNK),
    ('SOCK', stat.S_ISSOCK)
)
    result = []
    for fd in range(100):
        try:
            s = os.fstat(fd)
        except:
            continue
        for fd_type, func in _fd_types:
            if func(s.st_mode):
                break
        else:
            fd_type = str(s.st_mode)
        result.append((fd, fd_type))
    return result

def fd_table_status_logify(fd_table_result):
    return ('Open file handles: ' +
            ', '.join(['{0}: {1}'.format(*i) for i in fd_table_result]))

def fd_table_status_str():
    return fd_table_status_logify(fd_table_status())




#!/bin/python3
# coding: utf-8
def get_file_handles():
    """Build set of files that are in-use by processes.
       Requires 'handle.exe' from Microsoft SysInternals Suite.
       This seems to give a more complete list than using the psutil module.
    """

    from collections import OrderedDict
    import os
    import re
    import subprocess

    # Path to handle executable
    handle = "C:/Users/Jase/Downloads/SysinternalsSuite/handle.exe"

    # Get output string from 'handle'
    handle_str = subprocess.check_output([handle]).decode(encoding='ASCII')

    """ Build list of lists.
        1. Split string output, using '-' * 78 as section breaks.
        2. Ignore first section, because it is executable version info.
        3. Turn list of strings into a list of lists, ignoring first item (it's empty).
    """
    work_list = [x.splitlines()[1:] for x in handle_str.split(sep='-' * 78)[1:]]

    """ Build OrderedDict of pid information.
        pid_dict['pid_num'] = ['pid_name','open_file_1','open_file_2', ...]
    """
    pid_dict = OrderedDict()
    re1 = re.compile("(.*?\.exe) pid: ([0-9]+)")  # pid name, pid number
    re2 = re.compile(".*File.*\s\s\s(.*)")  # File name
    for x_list in work_list:
        key = ''
        file_values = []
        m1 = re1.match(x_list[0])
        if m1:
            key = m1.group(2)
    #        file_values.append(m1.group(1))  # pid name first item in list

        for y_strings in x_list:
            m2 = re2.match(y_strings)
            if m2:
                file_values.append(m2.group(1))
        pid_dict[key] = file_values

    # Make a set of all the open files
    values = []
    for v in pid_dict.values():
        values.extend(v)
    files_open = sorted(set(values))

    txt_file = os.path.join(os.getenv('TEMP'), 'lsof_handle_files')

    with open(txt_file, 'w') as fd:
        for a in sorted(files_open):
            fd.write(a + '\n')
    subprocess.call(['notepad', txt_file])
    os.remove(txt_file)

def get_parent_process():
        proc = psutil.Process()
        while proc.name() is not "pycharm.exe":
            proc = proc.parent()

        if not all([f.done() for f in self.futures]):
            procs = psutil.Process()
            print("Open files\n")
            print("---------------")
            print( "\n".join([f.path for f in proc.open_files()]))
            time.sleep(2)

def list_file_handles(proc=None):
    if proc is None:
        import psutil
        proc = psutil.Process()
    txt = ["Open files\n", "---------------"]
    lines = get_file_handle_list(proc)
    txt.extend(lines)
    return txt



def get_file_handle_list(proc):
    lines = [f.path for f in proc.open_files()]
    for child in proc.children():
        lines.extend(get_file_handle_list(child))
    return lines