from utils import create_empty_dir, walk
from utils.io import read_json, write_bin
from utils.parse import tokenize_page
from .simhashing import shingle, simhash, hamming_distance


def preprocess(src_path: str, path: str):
    """preprocess corpus from src_path for indexing and save to given path"""
    create_empty_dir(path)

    hashes = []
    total_count = 0
    unique_count = 0
    for file_path in walk(src_path, file_ext="json"):
        data = read_json(file_path)
        content = data["content"]
        tokens = list(
            tokenize_page(content, ["title", "h1", "h2", "h3", "strong", "b"])
        )
        shingles = shingle(list(token for token, _ in tokens), 2)
        h = simhash(shingles)
        total_count += 1
        for h2 in hashes:
            dist = hamming_distance(h, h2)
            if dist < 11:
                break
        else:
            unique_count += 1
            hashes.append(h)
            with open(f"{path}/{unique_count}.bin", "wb") as file:
                page = {"url": data["url"], "tokens": tokens}
                write_bin(file, page)
        if total_count % 1000 == 0:
            print(
                f"{total_count} seen, {unique_count} unique, {total_count-unique_count} deduplicated"
            )
