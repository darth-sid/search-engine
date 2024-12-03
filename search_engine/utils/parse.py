from collections.abc import Iterable, Iterator
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup
import re
import math

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

def compute_word_tf(tokens: Iterable[str]) -> dict[str,float]:
    '''return a map of tokens to their tf score (freq of token / total num of words)'''
    frequencies = {}
    total_words = 0
    for token in tokens:
        if token not in frequencies:
            frequencies[token] = 0
        frequencies[token] += 1
        total_words += 1
    tfs = {}
    for token, freq in frequencies.items():
        tfs[token] = math.log(freq + 1)
    return tfs
