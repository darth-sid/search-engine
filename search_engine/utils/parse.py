from collections.abc import Iterable, Iterator
from typing import Any
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup
import re
import math


def parse_html(html: str) -> BeautifulSoup:
    """returns raw textual content parsed from given html"""
    soup = BeautifulSoup(html, "lxml")
    return soup


def parse_xml(xml: str) -> BeautifulSoup:
    """returns raw textual content parsed from given html"""
    soup = BeautifulSoup(xml, "xml")
    return soup


def tokenize_page(
    content: str, important_tags: list[str], stem=True
) -> Iterator[tuple[str, str]]:
    """return a stream of tokens and their tag (if specified as important) from given page"""
    soup = (
        parse_xml(content)
        if content.lstrip().startswith("<?xml")
        else parse_html(content)
    )
    yield from tokenize_soup(soup, important_tags=important_tags, stem=stem)


def tokenize_soup(
    soup: BeautifulSoup, important_tags: list[str], stem=True
) -> Iterator[tuple[str, str]]:
    """return a stream of tokens and their tag (if specified as important) from given soup object"""
    for tag in important_tags:
        for element in soup.find_all(tag):
            yield from (
                (token, element.name) for token in tokenize(element.text, stem=stem)
            )
            element.decompose()
    yield from (
        (token, "") for token in tokenize(soup.get_text(separator=" "), stem=stem)
    )


def tokenize(text: str, stem=True) -> Iterator[str]:
    """return a stream of tokens from given text"""
    alnum_text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    for token in alnum_text.split():
        token = stem_word(token) if stem else token
        if token == "" or (token.isnumeric() and len(token) > 8):
            continue
        yield token


def shingle(features: list[str], k: int = 1) -> list[str]:
    return [" ".join(features[i : i + k]) for i in range(len(features) - k + 1)]


porter = PorterStemmer()


def stem_word(word: str) -> str:
    """return stem for given word"""
    return porter.stem(word)


def compute_word_tf(
    tokens: Iterable[tuple[str, str] | str],
) -> dict[str, dict[str, float]]:
    """return a map of tokens to their tf score split by tag (freq of token / total num of words)"""
    tokens = (((token, "") if isinstance(token, str) else token) for token in tokens)
    frequencies = {}
    for token, tag in tokens:
        if token not in frequencies:
            frequencies[token] = {}
        if tag not in frequencies[token]:
            frequencies[token][tag] = 0
        frequencies[token][tag] += 1
    tfs = {}
    for token in frequencies:
        tag_tfs = {}
        for tag in frequencies[token]:
            tag_tfs[tag] = math.log(frequencies[token][tag] + 1)
        tfs[token] = tag_tfs
    return tfs


if __name__ == "__main__":
    important_tags = ["title", "h1", "h2", "h3", "strong", "b"]
    content = "<title>titulo</title><div>hi<title>title</title><h1>header</h1><p>breh</p>oh</div>"
    print(list(tokenize_page(content, important_tags)))

    """important_tokens = []
    tokens = []
    for tag_type in ["title", "h1"]:
        for tag in soup.find_all(tag_type):
            for token in tokenize(tag.text):
                important_tokens.append(token)
            tag.decompose()
    tokens = list(tokenize(soup.get_text(separator=" ")))
    print(important_tokens)
    print(tokens)"""
