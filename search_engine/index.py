import os
from indexer import build_partials, merge_partials, preprocess
import timeit
import argparse

def build_index(src_path: str, index_path: str, partials_path: str):
    def test_build():
        build_partials(src_path, partials_path, 100)
    def test_merge():
        merge_partials(index_path, partials_path)

    print("Build Time:", timeit.timeit(test_build, globals=locals(), number=1))
    print("Merge Time: ", timeit.timeit(test_merge, globals=locals(), number=1))

if __name__ == "__main__":
    SRC = "CORPUS"
    PROCESSED = "PROCESSED"
    PARTIAL = "PARTIAL"
    INDEX = "INDEX"
    PART_THRESHOLD = 100

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pre", action="store_true")
    group.add_argument("--partial", action="store_true")
    group.add_argument("--merge", action="store_true")
    group.add_argument("--post", action="store_true")
    group.add_argument("--all", action="store_true")
    args = parser.parse_args()
    
    if args.pre:
        preprocess(SRC, PROCESSED)
        pass
    elif args.partial:
        build_partials(PROCESSED, PARTIAL, PART_THRESHOLD)
    elif args.merge:
        merge_partials(PARTIAL, INDEX)
    elif args.post:
        build_partials(PROCESSED, PARTIAL, PART_THRESHOLD)
        merge_partials(PARTIAL, INDEX)
    elif args.all:
        preprocess(SRC, PROCESSED)
        build_partials(PROCESSED, PARTIAL, PART_THRESHOLD)
        merge_partials(PARTIAL, INDEX)
    else:
        raise Exception
