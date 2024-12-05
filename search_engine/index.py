from indexer import build_partials, merge_partials, preprocess
import argparse

if __name__ == "__main__":
    SRC = "CORPUS"
    PROCESSED = "PROCESSED"
    PARTIAL = "PARTIAL"
    INDEX = "INDEX"
    PART_THRESHOLD = 100

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=False)
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
    else:
        preprocess(SRC, PROCESSED)
        build_partials(PROCESSED, PARTIAL, PART_THRESHOLD)
        merge_partials(PARTIAL, INDEX)
