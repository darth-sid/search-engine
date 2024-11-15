from collections.abc import Iterator
from .utils import parse_html, parse_file, tokenize, save
from .types import inverted_index
import os
from .linkedlist import SortedLinkedList

def build_partials(src_path: str, index_path: str, partials_path: str, part_threshold: int):
    index = {}
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
        save(partials_path, f"partition_{partition_id}", index)
    save(partials_path, "id_ref", ref)


def merge_partials(index_path: str, partials_path: str) -> None:
    for path in os.scandir(partials_path):
        pass

def index_page(index: inverted_index, path: str, doc_id: int) -> str:
    '''parse file at given path and update given inverted index'''
    data = parse_file(path)
    text = parse_html(data["content"])
    for word,tf in compute_word_tf(tokenize(text)).items():
        posting = (tf, doc_id)
        if word not in index:
            index[word] = SortedLinkedList()
        index[word].insert(posting)
    return data["url"]

def compute_word_tf(tokens: Iterator[str]) -> dict[str,float]:
    '''return a map of tokens to their tf score (freq of token / total num of words)'''
    frequencies = {}
    total_words = 0
    for token in tokens:
        if token not in frequencies:
            frequencies[token] = 0
        frequencies[token] += 1
        total_words += 1
    for word in frequencies:
        frequencies[word] = frequencies[word] / total_words
    return frequencies
