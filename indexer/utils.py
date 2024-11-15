from collections.abc import Iterator
import json
import pickle
from bs4 import BeautifulSoup
import re
from .types import inverted_index
from nltk.stem import PorterStemmer

def save(dir_path: str, name: str, struct: dict|list):
    with open(f"{dir_path}/{name}.bin", 'wb') as target:
        pickle.dump(struct, target)

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
