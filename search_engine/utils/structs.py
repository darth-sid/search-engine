from msgspec import Struct

class Posting(Struct):
    doc_id: int
    tf: float

class TermData(Struct):
    important_postings: list[Posting]
    postings: list[Posting]
    idf: float

