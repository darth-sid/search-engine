from utils.parse import tokenize
from utils.io import read_bin, read_bin_sized
from utils.structs import Posting, TermData
import heapq
import time

TAG_MULT = {"title": 5, "h1": 3, "h2": 2.5, "h3": 2, "strong": 1.5, "b": 1.5, "": 1}


def search_term(term: str) -> TermData | None:
    with open("./INDEX/offsets0.bin", "rb") as file:
        table = read_bin(file)
        pos, size = table[term[:2]]
    with open("./INDEX/offsets.bin", "rb") as file:
        table = read_bin_sized(file, pos, size)
        if term not in table:
            print(term)
            return None
        pos, size = table[term]
    with open("./INDEX/index.bin", "rb") as file:
        return read_bin_sized(file, pos, size, format=TermData)


def retrieve(query: str, n: int, timed=False) -> list | tuple[list, float]:
    start = time.time()

    q_terms = tokenize(query)

    # find documents containing all query terms
    results = {}
    for term in q_terms:
        if (data := search_term(term)) is not None:
            postings = data.postings
            temp_results = {}
            for posting in postings:
                doc_id = posting.doc_id
                score = 0
                for tag, tf in posting.tfs.items():
                    score += TAG_MULT[tag] * tf
                if not results or doc_id in results:
                    curr_score = results[doc_id] if doc_id in results else 0
                    temp_results[doc_id] = curr_score - score
            results = temp_results

    results_heap = []
    for doc_id in results:
        results_heap.append((results[doc_id], doc_id))
    heapq.heapify(results_heap)

    out = []
    with open("./INDEX/ids.bin", "rb") as file:
        urls = read_bin(file)
        for _ in range(n):
            if not results_heap:
                break
            _, doc_id = heapq.heappop(results_heap)
            out.append(urls[doc_id])

    end = time.time()
    if timed:
        return out, end - start
    return out
