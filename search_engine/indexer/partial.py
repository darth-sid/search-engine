from utils import create_empty_dir, walk
from utils.io import read_bin, write_bin
from utils.parse import compute_word_tf
from utils.structs import Posting
import sys

def build_partials(src_path: str, path: str, part_size: int):
    '''constructs partial indexes of size [part_size]MB from src path at given path'''
    create_empty_dir(path)

    partial_id = 0
    index_buf = PartialIndexWriteBuffer()
    for file_path in walk(src_path,file_ext="bin"):
        index_buf.index(file_path)
        if index_buf.size() >= part_size*1000000:
            index_buf.flush(f"{path}/part_{partial_id}.bin")
            partial_id += 1
    if index_buf:
        index_buf.flush(f"{path}/part_{partial_id}.bin")
    index_buf.flush_ids(f"{path}/ids.bin")

class PartialIndexWriteBuffer:
    '''write wrapper for partial indexes'''

    def __init__(self):
        self._table = {}
        self._urls = []
        self._counter = 0
        self._size = 0

    def size(self):
        '''returns estimate of size of current index in memory'''
        return self._size

    def index(self, path: str) -> None:
        '''index page from bin representation of form {url: [url], tokens: [tokens]}'''
        if not path.endswith("bin"):
            return

        with open(path, "rb") as file:
            data = read_bin(file)
            url = data["url"]
            tokens = data["tokens"]
            
        self._urls.append(url)
        for word,tf in compute_word_tf(tokens).items():
            posting = Posting(doc_id=self._counter, tf=tf)
            if word not in self._table:
                self._table[word] = []
                self._size += sys.getsizeof(word)
            self._table[word].append(posting)
            self._size += sys.getsizeof(posting)
        #print(self._counter, self._size / 1000000, data['url']) # TODO: delete
        self._counter += 1

    def flush(self, path: str) -> None:
        '''write current inverted index in memory to a bin file'''
        with open(path, "wb") as file:
            write_bin(file, sorted(self._table.items()), delimited=True) 
        self._table = {}
        self._size = 0

    def flush_ids(self, path: str) -> None:
        '''write id->url mappings to a bin file'''
        with open(path, "wb") as file:
            write_bin(file, self._urls)
        self._urls = []
