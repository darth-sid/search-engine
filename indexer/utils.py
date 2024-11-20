from collections.abc import Iterator
import json
import pickle
from bs4 import BeautifulSoup
import re
from nltk.stem import PorterStemmer
import struct

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
    with open(path, 'rb') as file:
        size = struct.unpack("<I", file.read(4))[0]
        val = pickle.loads(file.read(size))
        return val 

def save_as_binary(file_path: str, data: dict|list, delimited=False):
    file_path += ".bin"
    if isinstance(data, list) or not delimited:
        with open(file_path, 'wb') as file:
            pickle.dump(data, file)
    else:
        bin_data = b""
        for tup in data.items():
            serialized = pickle.dumps(tup)
            size = len(serialized)
            print(size)
            bin_data += (struct.pack("<I", size) + serialized)
        with open(file_path, 'wb') as file:
            file.write(bin_data)
        
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
    alnum_text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    for token in alnum_text.split():
        token = stem_word(token) if stem else token
        if token == "" or (token.isnumeric() and len(token) > 9):
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
    save_as_binary("test", test_dict, delimited=True)
    print(pop_term("test.bin"))
    print(pop_term("test.bin"))
    #print(len(pickle.dumps((1,2))))
