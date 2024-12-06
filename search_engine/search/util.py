from utils.parse import tokenize
from utils.io import read_bin, read_bin_sized
from utils.structs import Posting, TermData
import heapq
import time

def search_term(term: str) -> TermData|None:
    with open("./INDEX/offsets0.bin", "rb") as file:
        table = read_bin(file)
        pos,size = table[term[:2]]
    with open("./INDEX/offsets.bin", "rb") as file:
        table = read_bin_sized(file, pos, size)
        if term not in table:
            print(term)
            return None
        pos,size = table[term]
    with open("./INDEX/index.bin", "rb") as file:
        return read_bin_sized(file, pos, size, format=TermData)

def retrieve(query: str, n: int, timed=False) -> list|tuple[list,float]:
    start = time.time()

    q_terms = tokenize(query)

    results = {}
    for term in q_terms:
        data = search_term(term)
        if data is not None:
            postings = data.postings
            temp_results = {}
            for posting in postings:
                doc_id = posting.doc_id
                score = posting.tf * data.idf
                if doc_id == 18557:
                    print(term, posting.tf, data.idf)
                if not results:
                    temp_results[doc_id] = -1*score
                elif doc_id in results:
                    temp_results[doc_id] = results[doc_id]-score
            results = temp_results

    results_heap = []
    for doc_id in results:
        results_heap.append((results[doc_id],doc_id))
    heapq.heapify(results_heap)

    out = []
    with open("./INDEX/ids.bin", "rb") as file:
        table = read_bin(file)
        for _ in range(n):
            if not results_heap:
                break
            _, doc_id = heapq.heappop(results_heap)
            out.append(table[doc_id])

    end = time.time()
    if timed:
        return out,end-start
    return out
