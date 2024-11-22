import os
from indexer import build_partials, merge_partials
import timeit

def build_index(src_path: str="CORPUS", index_path: str="INDEX", partials_path: str="PARTIAL_INDEXES"):
    if os.path.exists(partials_path):
        for path in os.scandir(partials_path):
            os.remove(path)
    else:
        os.mkdir(partials_path)
    if os.path.exists(index_path):
        for path in os.scandir(index_path):
            os.remove(path)
    else:
        os.mkdir(index_path)
    
    def test_build():
        build_partials(src_path, partials_path, 100)
    def test_merge():
        merge_partials(index_path, partials_path)

    print(timeit.timeit(test_build, globals=locals(), number=1))
    print(timeit.timeit(test_merge, globals=locals(), number=1))

if __name__ == "__main__":
    build_index()
