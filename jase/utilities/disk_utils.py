import os, glob
import logging
import inspect

_path_cache = {}
logger = logging.getLogger("Disk Utiles")
logging.basicConfig(filename=r'P:/work/disk_remove.log',level=logging.DEBUG)

def remove(path, num_tries=1):
    """ Removes a file or directory, with a configurable number of retries.
    """


    # Turn off for debug
    #return False
    logger.info("Removing {}".format(path))

    if path in _path_cache:
        logger.error("This path {} is removed twice".format(path))
        (frame, filename, line_number, function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
        raise ValueError("Path was already removed by {}:{}".format(filename, line_number))
    else:
        print("Removing path", path)
        _path_cache[path] = True

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
