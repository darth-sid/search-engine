import os
import shutil

def create_empty_dir(path: str):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)

def copy(src_path: str, new_path: str):
    shutil.copy(src_path, new_path)
