from .utils import parse_html, parse_file, tokenize, save_as_binary, compute_word_tf
from .linkedlist import SortedLinkedList
from typing import NamedTuple
import pickle,struct
import os, sys
import heapq

class Posting(NamedTuple):
    tf: float
    id_: int

class PartialIndexReadObj:
    '''read wrapper for partial index bin files'''

    def __init__(self, path: str, part_id: int|None=None):
        self.id = int(path.split('_')[-1].rstrip(".bin")) if part_id is None else part_id
        self._file = open(path, 'rb')
        self._position = 0
        self._EOF = self._file.seek(0,2)

    def close(self) -> None:
        '''close file'''
        self._file.close()

    def read_next(self) -> tuple[str,list[Posting]]|None:
        '''read next chunk from bin file'''
        if self._position >= self._EOF:
            self.close()
            return None
        self._file.seek(self._position)
        size = struct.unpack("<I", self._file.read(4))[0]
        val = pickle.loads(self._file.read(size))
        self._position += size + 4
        return val

class PartialIndexWriteBuffer:
    '''write wrapper for partial indexes'''

    def __init__(self):
        self._table = {}
        self._urls = []
        self._counter = 0
        self._size = 0

    def size(self):
        return self._size

    def index_page(self, path: str) -> None:
        '''index page and store page's inverted index'''
        data = parse_file(path)
        text = parse_html(data["content"])
        self._urls.append(data["url"])
        for word,tf in compute_word_tf(tokenize(text)).items():
            posting = Posting(tf, self._counter)
            if word not in self._table:
                self._table[word] = []#SortedLinkedList() # TODO: fix
                self._size += sys.getsizeof(word)
            self._table[word].append(posting)
            self._size += sys.getsizeof(posting)
        print(self._counter, self._size) # TODO: delete
        self._counter += 1

    def flush(self, path: str, ref_path: str|None=None) -> None:
        '''write current contents to a bin file'''
        self._table = dict(sorted(self._table.items()))
        save_as_binary(path, self._table, delimited=True) 
        self._table = {}
        if ref_path is not None:
            save_as_binary(ref_path, self._ref)
            self._ref = []

def build_partials(src_path: str, path: str, part_threshold: int):
    '''constructs partial indexes for every [part_threshold] pages from src path at given path'''
    partial_id = 0
    index_buf = PartialIndexWriteBuffer()
    for domain in os.scandir(src_path):
        if not domain.is_dir():
            continue
        domain_path = f"{src_path}/{domain.name}"
        print(domain.name)

        for page in os.scandir(domain_path):
            if not page.is_file():
                continue
            file_path = f"{domain_path}/{page.name}"
            
            index_buf.index_page(file_path)
            if index_buf._counter % part_threshold == 0:
                index_buf.flush(f"{path}/part_{partial_id}")
                partial_id += 1
    if index_buf:
        index_buf.flush(f"{path}/part_{partial_id }", f"{path}/ids.bin")

def merge_partials(path: str, partials_path: str) -> None:
    '''merges partial index from partials path into a single index and lookup table at given path'''

    os.rename(f"{partials_path}/ids.bin", f"{path}/ids.bin")
    partials = {}
    for partial in os.scandir(partials_path):
        if partial.name.startswith("id_"):
            continue
        else:
            partial = PartialIndexReadObj(f"{partials_path}/{partial.name}")
            partials[partial.id] = partial

    heap = []
    class Entry(NamedTuple):
        term: str
        postings: list[Posting]
        src_id: int

    for partial in partials:
        term, postings = partial.read_next()
        heapq.heappush(heap, Entry(term,postings,partial.id))



    def pop_term() -> Entry:
        '''pop term-postings pair from heap and try to repopulate with a 
        term-postings pair from same partial index'''
        entry = heapq.heappop(heap)
        if (tup:=partials[entry.src_id].read_next()) is not None:
            term,postings = tup
            heapq.heappush(heap, Entry(term, postings, entry.src_id))
        return entry

    term_position_table = {}
    with open(f"{path}/index.bin", "wb") as index:
        pos = 0
        while heap:
            print(len(heap))

            term,postings,_ = pop_term()
            print(term)
            while heap and heap[0].term == term:
                entry = pop_term()
                postings.extend(entry.postings)

            serialized_postings = pickle.dumps(postings)
            size = len(serialized_postings)
            term_position_table[term] = (pos,size)
            index.seek(pos)
            index.write(serialized_postings)
            pos += size

    with open(f"{path}/offsets.bin", "wb") as file:
        pickle.dump(term_position_table, file)

if __name__ == "__main__":
    merge_partials("INDEX", "PARTIAL_INDEXES")
