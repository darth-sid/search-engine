from collections.abc import Iterator
from .utils import parse_html, parse_file_content, tokenize
from .types import inverted_index

def index_page(index: inverted_index, path: str) -> None:
    '''parse file at given path and update given inverted index'''

    text = parse_html(parse_file_content(path))
    for word,tf in compute_word_tf(tokenize(text)).items():
        posting = (tf, path)
        if word not in index:
            index[word] = []
        index[word].append(posting)

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
