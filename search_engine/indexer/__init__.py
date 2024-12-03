from utils import create_empty_dir, copy
from utils.io import read_json, read_bin, read_bin_chunk, write_bin
from utils.parse import parse_html, parse_xml, tokenize, compute_word_tf
from typing import NamedTuple
import os
import sys
import heapq
from .simhashing import shingle, simhash, hamming_distance


class PartialIndexReadObj:
    '''read wrapper for partial index bin files'''

    def __init__(self, path: str, part_id: int|None=None):
        self.id = int(path.split('_')[-1].rstrip(".bin")) if part_id is None else part_id
        self._file = open(path, 'rb')
        self._pos = 0
        self._EOF = self._file.seek(0,2)

    def close(self) -> None:
        '''close file'''
        self._file.close()

    def read_next(self) -> tuple[str,list[tuple]]|None:
        '''read next chunk from bin file'''
        if self._pos >= self._EOF:
            self.close()
            return None
        val, size = read_bin_chunk(self._file, pos=self._pos)
        self._pos += size
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

    def index_page_json(self, path: str) -> None:
        '''index page from json form'''
        if not path.endswith("json"):
            return
        #print(path)
        data = read_json(path)
        content = data["content"]
        text = parse_xml(content) if content.lstrip().startswith("<?xml") else parse_html(content)
        tokens = list(tokenize(text))
        self.index_page_from_tokens(data["url"], tokens)

    def index_page_bin(self, path: str) -> None:
        '''index page from bin form'''
        if not path.endswith("bin"):
            return

        with open(path, "rb") as file:
            data = read_bin(file)
        self.index_page_from_tokens(data["url"], data["tokens"])
            

    def index_page_from_tokens(self, url: str, tokens: list[str]) -> None:
        '''score page based on its tokens and store it'''
        self._urls.append(url)
        for word,tf in compute_word_tf(tokens).items():
            posting = (tf, self._counter)
            if word not in self._table:
                self._table[word] = []
                self._size += sys.getsizeof(word)
            self._table[word].append(posting)
            self._size += sys.getsizeof(posting)
        #print(self._counter, self._size / 1000000, data['url']) # TODO: delete
        self._counter += 1


    def flush(self, path: str, ref_path: str|None=None) -> None:
        '''write current contents to a bin file'''
        with open(path, "wb") as file:
            write_bin(file, sorted(self._table.items()), delimited=True) 
        self._table = {}
        self._size = 0
        if ref_path is not None:
            with open(ref_path, "wb") as file:
                write_bin(file, self._urls)
            self._urls = []

def preprocess(src_path: str, path: str):
    '''preprocess corpus from src_path for indexing and save to given path'''
    create_empty_dir(path)

    hashes = []
    c = 0
    for domain in os.scandir(src_path):
        if not domain.is_dir():
            continue
        domain_path = f"{src_path}/{domain.name}"
        print(domain_path)
        s = c
        sh = len(hashes)
        for page in os.scandir(domain_path):
            if not page.is_file():
                continue
            file_path = f"{domain_path}/{page.name}"
            if not file_path.endswith("json"):
                continue
            
            data = read_json(file_path)
            content = data["content"]
            text = parse_xml(content) if content.lstrip().startswith("<?xml") else parse_html(content)
            tokens = list(tokenize(text))
            shingles = shingle(tokens, 2)
            h = simhash(shingles)
            c += 1
            for h2 in hashes:
                dist = hamming_distance(h, h2)
                if dist < 11:
                    break
            else:
                hashes.append(h)
                dir_path = f"{path}/{domain.name}"
                if not os.path.exists(dir_path):
                    os.mkdir(dir_path)
                file_name = page.name.split(".")[0] + ".bin"
                with open(f"{dir_path}/{file_name}", "wb") as file:
                    page = {"url": data["url"], "tokens": tokens}
                    write_bin(file, page)
        print(f"{c} total", f"{len(hashes)} unique", f"{c-len(hashes)} deduplicated")
        print(f"{c-s} total new", f"{len(hashes)-sh} new unique", f"{(c-s)-(len(hashes)-sh)} new deduplicated")

def build_partials(src_path: str, path: str, part_size: int):
    '''constructs partial indexes of size [part_size]MB from src path at given path'''
    create_empty_dir(path)

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
            
            index_buf.index_page_bin(file_path)
            if index_buf.size() >= part_size*1000000:
                index_buf.flush(f"{path}/part_{partial_id}.bin")
                partial_id += 1
    if index_buf:
        index_buf.flush(f"{path}/part_{partial_id}.bin", f"{path}/ids.bin")

def merge_partials(partials_path: str, path: str) -> None:
    '''merges partial index from partials path into a single index and lookup table at given path'''
    create_empty_dir(path)
    copy(f"{partials_path}/ids.bin", f"{path}/ids.bin")

    partials = {}
    partial_ids = []
    for partial in os.scandir(partials_path):
        if not partial.name.startswith("part_"):
            continue
        else:
            partial = PartialIndexReadObj(f"{partials_path}/{partial.name}")
            partials[partial.id] = partial
            partial_ids.append(partial.id)
    partial_ids.sort()

    heap = []
    class Entry(NamedTuple):
        term: str
        postings: list[tuple]
        src_id: int
    print(partials)
    for p_id in partial_ids:
        partial = partials[p_id]
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

    offsets = {}
    with open(f"{path}/index.bin", "wb") as index:
        pos = 0
        while heap:
            term,postings,_ = pop_term()
            while heap and heap[0].term == term:
                entry = pop_term()
                postings.extend(entry.postings)
            size = write_bin(index, postings, pos=pos)
            frag = term[:2]
            if frag not in offsets:
                offsets[frag] = {}
            offsets[frag][term] = (pos,size)
            pos += size

    offsets_offsets = {}
    with open(f"{path}/offsets.bin", "ab") as file:
        pos = 0
        for frag in offsets:
            size = write_bin(file, offsets[frag])
            offsets_offsets[frag] = (pos,size)
            pos += size

    with open(f"{path}/offsets0.bin", "wb") as file:
        write_bin(file, offsets_offsets)
