from collections.abc import Iterator
from .utils import parse_html, parse_file, tokenize, save_as_binary
from .custom_types import inverted_index
import os
from indexer.utils import PartialIndexBuffer

def build_partials(src_path: str, index_path: str, partials_path: str, part_threshold: int):
    id_path = f"{index_path}/id_ref"
    os.mkdir(id_path)
    index_buf = PartialIndexBuffer(partials_path, id_path)
    partition_count = 0
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
                index_buf.flush(str(partition_count), str(partition_count))
                partition_count += 1
    if index_buf:
        index_buf.flush(str(partition_count), str(partition_count))
            
'''    index = {}
    ref = []
    doc_id = 0
    partition_id = 0
    id_path = f"{partials_path}/id_map"
    os.mkdir(id_path)
    for domain in os.scandir(src_path):
        if not domain.is_dir(): 
            continue
        domain_path = f"{src_path}/{domain.name}"
        print(domain.name)

        for page in os.scandir(domain_path):
            print(doc_id)
            if not page.is_file():
                continue
            file_path = f"{domain_path}/{page.name}"

            ref.append(index_page(index, file_path, doc_id))
            doc_id += 1
            if doc_id % part_threshold == 0:
                for term in index:
                    index[term] = list(index[term])
                save(partials_path, str(partition_id), index)
                save(id_path, str(partition_id), ref)
                index = {}
                ref = []
                partition_id += 1
    if index:
        for term in index:
            index[term] = list(index[term])
        save(partials_path, str(partition_id), index)
    if ref:
        save(partials_path, str(partition_id), ref)
'''

def merge_partials(index_path: str, partials_path: str) -> None:
    for path in os.scandir(partials_path):
        pass #TODO: pull term merge all postings and repeat

'''def index_page(index: inverted_index, path: str, doc_id: int) -> str:
    ''parse file at given path and update given inverted index''
    data = parse_file(path)
    #print(data["encoding"])
    text = parse_html(data["content"])
    for word,tf in compute_word_tf(tokenize(text)).items():
        posting = (tf, doc_id)
        if word not in index:
            index[word] = SortedLinkedList()
        index[word].insert(posting)
    return data["url"]

'''
