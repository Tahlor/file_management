from pathlib import Path
import os
import pywintypes, win32file, win32con
from tqdm import tqdm

"""
This copies all of the created, modified, and access times from one folder structure over to a mirrored one

Usage:

python mirror_file_times.py /src/dir /dest/dir

"""

def change_windows_file_times(fname, creation_time=None, access_time=None, modified_time=None):
    """
    Args:
        fname (str/Path): Path of file to have new time
        creation_time (int, Unix Epoch Time): New creation time
        access_time (int, Unix Epoch Time): New access time
        modified_time (int, Unix Epoch Time): New modified time
    Returns:
        dict: new times from filesystem

    """
    creation_time = pywintypes.Time(creation_time)
    access_time = creation_time if access_time is None else pywintypes.Time(access_time)
    modified_time= creation_time if modified_time is None else pywintypes.Time(modified_time)
    fname = str(fname)
    if os.path.isfile(fname):
        winfile = win32file.CreateFile(
            fname, win32con.GENERIC_WRITE,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
            None, win32con.OPEN_EXISTING,
            win32con.FILE_ATTRIBUTE_NORMAL, None)
    elif os.path.isdir(fname):
        winfile = win32file.CreateFile(
            fname, win32con.GENERIC_WRITE,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
            None, win32con.OPEN_EXISTING,
            win32con.FILE_FLAG_BACKUP_SEMANTICS, None)
    win32file.SetFileTime(winfile, CreationTime=creation_time, LastAccessTime=access_time, LastWriteTime=modified_time)
    winfile.close()
    file_stats = os.stat(fname)

    # Output stats
    return {'accessed': file_stats.st_atime, 'modified': file_stats.st_mtime, 'created': file_stats.st_ctime}

def change_linux_file_times(fname, access_time, modified_time, *args, **kwargs):
    """ Not tested
    
    Args:
        fname (str/Path): Path of file to have new time
        access_time (int, Unix Epoch Time): New access time
        modified_time (int, Unix Epoch Time): New modified time
    Returns:
        dict: new times from filesystem

    """
    os.utime(fname, (access_time, modified_time))
    file_stats = os.stat(fname)

    # Output stats
    return {'accessed': file_stats.st_atime, 'modified': file_stats.st_mtime, 'created': file_stats.st_ctime}

def compare_files(s, d, windows=True):
    """

    Args:
        s (str/Path): source file (with correct date)
        d (str/Path): destination file (date to be overwritten)
        windows (bool): True if OS=Windows

    Returns:

    """
    s_stat = os.stat(s)
    d_stat = os.stat(d)
    if s_stat.st_ctime!=d_stat.st_ctime or s_stat.st_mtime!=d_stat.st_mtime or s_stat.st_atime!=d_stat.st_atime:
        try:
            if windows:
                change_windows_file_times(d, creation_time=s_stat.st_ctime,
                                          modified_time=s_stat.st_mtime,
                                          access_time=s_stat.st_atime)
            else:
                change_linux_file_times(d,modified_time=s_stat.st_mtime,
                                          access_time=s_stat.st_atime)
        except Exception as e:
            print(s, e)

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('src')  # positional arg
    parser.add_argument('dest')
    parser.add_argument('--linux', action="store_true")  # store true if specified; binary flag argumuent
    opts = parser.parse_args()

    # Source
    opts.src = Path(opts.src)
    opts.dest = Path(opts.dest)
    opts.linux = True

    for f in tqdm(list(opts.src.rglob("*"))):
        equiv_file = opts.dest / f.relative_to(opts.src)
        if Path(equiv_file).exists():
            compare_files(f, equiv_file, windows=not opts.linux)

