import os
import shutil
from collections.abc import Iterator

def create_empty_dir(path: str):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)

def copy(src_path: str, new_path: str):
    shutil.copy(src_path, new_path)

def walk(dir_path: str, *, file_ext: str|None=None) -> Iterator:
    for path in os.scandir(dir_path):
        if path.is_dir():
            yield from walk(path.path, file_ext=file_ext)
        elif path.is_file():
            if file_ext is None or path.name.endswith(file_ext):
                yield path.path
        else:
            continue
