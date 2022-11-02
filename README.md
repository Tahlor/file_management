# file_management
Collection of scripts to help with managing files.


# Mirror File Times
If you've already copied a folder over but want to modify file times, you can run this Python script to update the creation/modified/access times to mirror the original source.

Usage: `python mirror_file_times.py /src/dir /dest/dir`

Installation (Python 3.7+): `pip install pypiwin32 tqdm`

It should work on Linux, but I haven't tested it.

