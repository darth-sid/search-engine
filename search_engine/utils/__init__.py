from collections.abc import Sequence, Collection, Iterable, Iterator
from typing import BinaryIO, Any
import orjson
import pickle
from bs4 import BeautifulSoup
import re
from nltk.stem import PorterStemmer
import struct

def compute_word_tf(tokens: Iterable[str]) -> dict[str,float]:
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
    frequencies = dict(sorted(frequencies.items()))
    #print(frequencies)
    return frequencies

def pop_term(path: str):
    with open(path, 'rb') as file:
        size = struct.unpack("<I", file.read(4))[0]
        val = pickle.loads(file.read(size))
        return val 

def write(file: BinaryIO, data: Collection, pos: int|None=None, delimited: bool=False) -> int:
    '''serializes a sequence and writes it to a given file + returns size of written chunk'''
    if pos is not None and pos!=file.tell():
        file.seek(pos)
    if not delimited:
        serialized = pickle.dumps(data)
    else:
        bin_data = []
        for i,elem in enumerate(data):
            serialized = pickle.dumps(elem)
            size = len(serialized)
            #print(f"{i*100/len(data)}%")
            bin_data.append(struct.pack("<I", size))
            bin_data.append(serialized)
        serialized = b"".join(bin_data)
    file.write(serialized)
    return len(serialized)


def read(file: BinaryIO, pos: int|None=None, delimited: bool=False) -> tuple[int,Any]:
    '''deserializes a chunk from a binary file obj and returns its size and value'''
    if pos is not None and pos != file.tell():
        file.seek(pos)
    if delimited:
        size = struct.unpack("<I", file.read(4))[0]
        chunk = file.read(size)
        size += 4
    else:
        chunk = file.read()
        size = len(chunk)
    return size,pickle.loads(chunk)

def parse_html(html: str):
    '''returns raw textual content parsed from given html'''
    soup = BeautifulSoup(html, 'lxml')
    raw_text = soup.get_text(separator=" ", strip=True)
    return raw_text

def parse_xml(xml: str):
    '''returns raw textual content parsed from given html'''
    soup = BeautifulSoup(xml, 'xml')
    raw_text = soup.get_text(separator=" ", strip=True)
    return raw_text

def parse_file(path: str) -> dict[str,str]:
    '''extracts html content from file'''
    with open(path, 'r') as file:
        return orjson.loads(file.read())

def tokenize(text: str, stem=True) -> Iterator[str]:
    '''return a stream of tokens from file at given path'''
    alnum_text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    for token in alnum_text.split():
        token = stem_word(token) if stem else token
        if token == "" or (token.isnumeric() and len(token) > 8):
            continue
        yield token

porter = PorterStemmer()
def stem_word(word: str) -> str:
    '''return stem for given word'''
    return porter.stem(word)
