import os
from pathlib import Path

def is_file_descriptor(fd):
    try:
        # check if fd is an integer
        if isinstance(fd, int):
            # try to get file status
            os.fstat(fd)
            return True
    except (TypeError, ValueError, OSError):
        return False
    return False

def is_file_path(path):
    return isinstance(path, str) and os.path.exists(path)
