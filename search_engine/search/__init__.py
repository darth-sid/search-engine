import pickle
import heapq
from utils import tokenize, read
import time

def search_term(term: str) -> list:
    with open("./INDEX/offsets0.bin", "rb") as file:
        table = pickle.load(file)
        pos,size = table[term[:2]]
    with open("./INDEX/offsets.bin", "rb") as file:
        file.seek(pos)
        table = pickle.loads(file.read(size))
        if term not in table:
            print(term)
            return []
        pos,size = table[term]
    with open("./INDEX/index.bin", "rb") as file:
        file.seek(pos)
        postings = pickle.loads(file.read(size))
    return postings



def retrieve(query: str, n: int):
    q_terms = tokenize(query)
    results = {}
    for term in q_terms:
        postings = search_term(term)
        for score,doc_id in postings:
            if doc_id not in results:
                results[doc_id] = 0
            results[doc_id] -= score
    results_heap = []
    for doc_id in results:
        results_heap.append((results[doc_id],doc_id))
    heapq.heapify(results_heap)
    out = []
    with open("./INDEX/ids.bin", "rb") as file:
        table = pickle.load(file)
        for _ in range(n):
            if not results_heap:
                break
            _, doc_id = heapq.heappop(results_heap)
            out.append(table[doc_id])
    return out
