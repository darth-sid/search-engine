from collections.abc import Iterator
import json
import pickle
from bs4 import BeautifulSoup
import re
from nltk.stem import PorterStemmer
import struct
from .linkedlist import SortedLinkedList


class PartialIndexBuffer:
    def __init__(self, partials_path: str, ref_path: str):
        self._table = {}
        self._ref = []
        self._counter = 0 
        self._len = 0
        self.partials_path = partials_path
        self.ref_path = ref_path

    def __len__(self):
        return self._len

    def index_page(self, path: str):
        data = parse_file(path)
        text = parse_html(data["content"])
        self._ref.append(data["url"])
        for word,tf in compute_word_tf(tokenize(text)).items():
            posting = (tf, self._counter)
            if word not in self._table:
                self._table[word] = SortedLinkedList()
            self._table[word].insert(posting)
        print(self._counter, self._len)
        self._counter += 1
        self._len += 1

    def read(self, path: str):
        pass

    def flush(self, partition_file_name, ref_file_name):
        for term in self._table:
            self._table[term] = list(self._table[term])
        save_as_binary(self.partials_path, partition_file_name, self._table) 
        save_as_binary(self.ref_path, ref_file_name, self._ref)
        self._ref = []
        self._table = {}
        self._len = 0



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
    frequencies = dict(sorted(frequencies.items()))
    #print(frequencies)
    return frequencies

def pop_term(path: str):
    pass

def save_as_binary(dir_path: str, name: str, data: dict|list, delimited=False):
    file_name = f"{dir_path}/{name}.bin"
    if isinstance(data, list) or not delimited:
        with open(file_name, 'wb') as file:
            pickle.dump(data, file)
    else:
        for tup in data.items():
            serialized = pickle.dumps(tup)
            size = len(serialized)
            with open(file_name, 'wb') as file:
                file.write(struct.pack('<I', size))
                file.write(serialized)
        
def parse_html(html: str):
    '''returns raw textual content parsed from given html'''
    soup = BeautifulSoup(html, 'html.parser')
    raw_text = soup.get_text(separator=" ", strip=True)
    return raw_text

def parse_file(path: str) -> dict[str,str]:
    '''extracts html content from file'''
    with open(path, 'r') as file:
        return json.load(file)

def tokenize(text: str, stem=True) -> Iterator[str]:
    '''return a stream of tokens from file at given path'''
    alnum_text = re.sub(r"[^a-z0-9\s]", "", text.lower())
    for token in alnum_text.split():
        token = stem_word(token) if stem else token
        if token == "":
            continue
        yield token

porter = PorterStemmer()
def stem_word(word: str) -> str:
    '''return stem for given word'''
    return porter.stem(word)

if __name__ == "__main__":

    test_dict = {'hello':[1,2,3],
                 'why':[1,2,3,4,5,6,7,8,9],
                 'supercalifragilistic':[1,2],
                 'volcanicosteoporosis':[1,3,5,6,7,8,9,10,11,12,13]
                 }
    save_as_binary(".", "test", test_dict)
    print(pop_term("test.bin"))
    print(len(pickle.dumps((1,2))))
