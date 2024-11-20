from collections.abc import Iterator
from .utils import parse_html, parse_file, tokenize, save_as_binary, compute_word_tf
from .custom_types import inverted_index
import os
from .linkedlist import SortedLinkedList
import struct
import pickle
import heapq

class IdTable:
    def __init__(self, paths: list, partition_size: int):
        self._paths = sorted(paths, key=lambda path: int(path.split('_')[-1].rstrip(".bin")))
        self._part_size = partition_size

    def __getitem__(self, page_id):
        path = self._paths[(page_id // self._part_size)]
        with open(path, 'rb') as file:
            table = pickle.load(file)
            return table[page_id % self._part_size]

    def write(self, target_path: str):
        urls = []
        c = 0
        for path in self._paths:
            with open(path, 'rb') as file:
                mini_table = pickle.load(file)
                for val in mini_table:
                    urls.append(val)
            c += 1
        with open(target_path, 'wb') as file:
            file.write(pickle.dumps(urls))


class PartialIndexReadObj:
    def __init__(self, path: str):
        self.id = int(path.split('_')[-1].rstrip(".bin"))
        self._file = open(path, 'rb')
        self._position = 0

    def close(self):
        self._file.close()

    def read_next(self):
        try:
            self._file.seek(self._position)
            size = struct.unpack("<I", self._file.read(4))[0]
            val = pickle.loads(self._file.read(size))
            self._position += size + 4
            #print(val)
            #print(self._file.name, self._position, val[0])
            return val
        except Exception as e:
            print(e)
            return None

class PartialIndexWriteBuffer:
    def __init__(self):
        self._table = {}
        self._ref = []
        self._counter = 0 
        self._len = 0

    def __len__(self):
        return self._len

    def index_page(self, path: str):
        data = parse_file(path)
        text = parse_html(data["content"])
        self._ref.append(data["url"])
        for word,tf in compute_word_tf(tokenize(text)).items():
            posting = (tf, self._counter)
            if word not in self._table:
                self._table[word] = []#SortedLinkedList()
            self._table[word].append(posting)
        print(self._counter, self._len)
        self._counter += 1
        self._len += 1

    def flush(self, path: str, ref_path: str):
        self._table = dict(sorted(self._table.items()))
        #for term in self._table:
        #    self._table[term] = list(self._table[term])
        save_as_binary(path, self._table, delimited=True) 
        save_as_binary(ref_path, self._ref)
        self._ref = []
        self._table = {}
        self._len = 0

def build_partials(src_path: str, index_path: str, partials_path: str, part_threshold: int):
    i = 0
    id_path = f"{index_path}/id_ref"
    os.mkdir(id_path)
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
            if len(index_buf) == part_threshold:
                index_buf.flush(f"{partials_path}/part_{i}", f"{partials_path}/id_{i}")
                i += 1
            #if i > 4:
            #    return
    if index_buf:
        index_buf.flush(f"{partials_path}/part_{i}", f"{partials_path}/id_{i}")

def merge_partials(index_path: str, partials_path: str) -> None:
    id_ref_paths = []
    partitions = []

    for path in os.scandir(partials_path):
        if path.name.startswith("id_"):
            id_ref_paths.append(f"{partials_path}/{path.name}")
        else:
            partitions.append(PartialIndexReadObj(f"{partials_path}/{path.name}"))
            #os.remove(f"{partials_path}/{path.name}")
    partitions.sort(key=lambda partition: partition.id)


    id_table = IdTable(id_ref_paths, 1000)

    heap = []
    for i,partition in enumerate(partitions):
        heapq.heappush(heap, (partition.read_next(),i))
    
    def pop_term():
        val,i = heapq.heappop(heap)
        term,postings = val
        new_val = partitions[i].read_next()
        #print(new_val)
        if new_val is not None:
            heapq.heappush(heap, (new_val, i))

        return term, postings

    term_table = {}
    with open(f"{index_path}/index.bin", "wb") as file:
        pos = 0
        while heap:
            print(len(heap))

            term,postings = pop_term()
            print(term)
            while heap and heap[0][0][0] == term:
                _,more_postings = pop_term()
                postings.extend(more_postings)

            try:
                serialized_postings = pickle.dumps(postings)
                size = len(serialized_postings)
                term_table[term] = (pos,size)
                file.seek(pos)
                file.write(serialized_postings)
                pos += size
            except OSError as e:
                print(e)
    id_table.write(f"{index_path}/ids.bin")
    with open(f"{index_path}/offsets.bin", "wb") as file:
        file.write(pickle.dumps(term_table))


if __name__ == "__main__":
    merge_partials("INDEX", "PARTIAL_INDEXES")
