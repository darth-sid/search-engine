from msgspec import Struct


class Posting(Struct):
    doc_id: int
    tfs: dict[str, float]


class PageData(Struct):
    url: str
    tokens: list[tuple[str, str]]
    bigrams: list[str]
