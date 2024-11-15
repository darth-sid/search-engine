import os, shutil
from indexer import build_partials, merge_partials

def build_index(src_path: str="CORPUS", index_path: str="INDEX", partials_path: str="PARTIAL_INDEXES", part_threshold: int=1000):
    os.mkdir(partials_path)

    build_partials(src_path, index_path, partials_path, part_threshold)
    
    merge_partials(index_path, partials_path)

    #shutil.rmtree(partials_path)
    
if __name__ == "__main__":
    build_index()
