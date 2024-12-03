import heapq
from utils.parse import tokenize
from utils.io import read_bin, read_bin_sized
import time

def search_term(term: str) -> list:
    with open("./INDEX/offsets0.bin", "rb") as file:
        table = read_bin(file)
        pos,size = table[term[:2]]
    with open("./INDEX/offsets.bin", "rb") as file:
        table = read_bin_sized(file, pos, size)
        if term not in table:
            print(term)
            return []
        pos,size = table[term]
    with open("./INDEX/index.bin", "rb") as file:
        postings = read_bin_sized(file, pos, size)
    return postings

def retrieve(query: str, n: int, timed=False) -> list|tuple[list,float]:
    start = time.time()

    q_terms = tokenize(query)
    results = {}
    first = True
    for term in q_terms:
        postings = search_term(term)
        temp_results = {}
        for score,doc_id in postings:
            if first:
                temp_results[doc_id] = -1*score
            elif doc_id in results:
                temp_results[doc_id] = results[doc_id]-score
        results = temp_results
        first = False
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
