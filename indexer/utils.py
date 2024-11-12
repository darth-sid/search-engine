from collections.abc import Iterator
import json
from bs4 import BeautifulSoup
import re
from .types import inverted_index

def save_index_json(dir_path: str, name: str, index: inverted_index):
    with open(f"{dir_path}/{name}.json", 'w') as index_json:
        json.dump(index, index_json)

def parse_html(html: str):
    '''returns raw textual content parsed from given html'''
    soup = BeautifulSoup(html, 'html.parser')
    raw_text = soup.get_text(separator=" ", strip=True).lower()
    return raw_text 

def parse_file_content(path: str) -> str:
    '''extracts html content from file'''
    with open(path, 'r') as file:
        return json.load(file)['content']

def tokenize(text: str) -> Iterator[str]:
    '''return a stream of tokens from file at given path'''
    alnum_text = re.sub(r"[^a-z0-9\s]", "", text)
    for token in alnum_text.split():
        token = stem(token)
        if token == "":
            continue
        yield token

def stem(word: str) -> str:
    '''return stem for given word'''
    return word
