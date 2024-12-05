from msgspec import Struct

class Posting(Struct):
    doc_id: int
    tf: float

class TermData(Struct):
    postings: list[Posting]
    idf: float

