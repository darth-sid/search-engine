from utils import create_empty_dir, walk
from utils.io import read_bin, write_bin
from utils.parse import compute_word_tf
from utils.structs import PageData, Posting
from typing import Iterable
import sys


def build_partials(src_path: str, path: str, part_size: int):
    """constructs partial indexes of size [part_size]MB from src path at given path"""
    create_empty_dir(path)

    partial_id = 0
    index_buf = PartialIndexWriteBuffer()
    doc_num = 0
    urls = []
    for file_path in walk(src_path, file_ext="bin"):
        with open(file_path, "rb") as file:
            data = read_bin(file, format=PageData)
        urls.append(data.url)
        index_buf.index(doc_num, data.tokens)
        index_buf.index(doc_num, data.bigrams)
        if index_buf.size() >= part_size * 1000000:
            index_buf.flush(f"{path}/{partial_id}.bin")
            partial_id += 1
        doc_num += 1
    if index_buf:
        index_buf.flush(f"{path}/{partial_id}.bin")
    with open(f"{path}/ids.bin", "wb") as file:
        write_bin(file, urls)


class PartialIndexWriteBuffer:
    """write wrapper for partial indexes"""

    def __init__(self):
        self._table = {}
        self._size = 0

    def size(self):
        """returns estimate of size of current index in memory"""
        return self._size

    def index(self, doc_id: int, tokens: Iterable[tuple[str, str] | str]):
        """index page from a list of token-tag pairs"""
        for token, tfs in compute_word_tf(tokens).items():
            posting = Posting(doc_id=doc_id, tfs=tfs)
            if token not in self._table:
                self._table[token] = []
                self._size += sys.getsizeof(token)
            self._table[token].append(posting)
            self._size += sys.getsizeof(posting)

    def flush(self, path: str) -> None:
        """write current inverted index in memory to a bin file"""
        with open(path, "wb") as file:
            write_bin(file, sorted(self._table.items()), delimited=True)
        self._table = {}
        self._size = 0
