import os, glob
import logging
import inspect

def remove(path, num_tries=1):
    """ Removes a file or directory, with a configurable number of retries.
    """
    if os.path.isfile(path):
        remove_file(path, num_tries=num_tries)
    elif os.path.isdir(path):
        # Make sure the directory is empty
        for file_or_dir in glob.glob(path + "/*"):
            remove(file_or_dir, num_tries=num_tries)
        os.rmdir(path)
    else:
        raise ValueError("Can't remove {}:  This isn't a valid file or directory.".format(path))

def remove_file(path, num_tries=1):
    i=0
    while True:
        try:
            i += 1
            os.remove(path)
            break
        except PermissionError as e:
            if i < num_tries:
                import time
                time.sleep(.1)
            else:
                raise
    return True
