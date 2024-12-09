from utils.parse import tokenize, shingle
from utils.io import read_bin, read_bin_sized
from utils.structs import Posting
import heapq
import time

TAG_MULT = {"title": 10, "h1": 6, "h2": 4, "h3": 2, "strong": 1.5, "b": 1.5, "": 1}


def search_term(term: str) -> list[Posting]:
    with open("INDEX/offsets_offsets.bin", "rb") as file:
        table = read_bin(file)
        pos, size = table[term[:3]]
    with open("INDEX/offsets.bin", "rb") as file:
        table = read_bin_sized(file, pos, size)
        if term not in table:
            raise Exception(f"{term} not in corpus")
        pos, size = table[term]
    with open("INDEX/index.bin", "rb") as file:
        return read_bin_sized(file, pos, size, format=list[Posting])


def get_idfs(terms: list[str]) -> dict[str, float]:
    with open("INDEX/idf_offsets.bin", "rb") as file:
        offset_table = read_bin(file)
    with open("INDEX/idf.bin", "rb") as file:
        idfs = {}
        for term in terms:
            pos, size = offset_table[term[:3]]
            table = read_bin_sized(file, pos, size)
            if term not in table:
                continue
            idfs[term] = table[term]
        return idfs


def retrieve(query: str, n: int, timed=False) -> list | tuple[list, float]:
    start = time.time()

    # get terms and bigrams
    q_terms = list(tokenize(query))
    bigrams = shingle(q_terms, 2)

    # get term idfs
    idfs = get_idfs(q_terms)
    q_terms = list(idfs.keys())  # only words that exist in corpus

    # calculate bigram idfs as sum of term idfs
    q_bigrams = []
    for bigram in bigrams:
        term1, term2 = bigram.split()
        if term1 in idfs and term2 in idfs:
            idfs[bigram] = idfs[term1] + idfs[term2]
            q_bigrams.append(bigram)  # only bigrams that exist in corpus

    # unigrams in order of descending rarity followed by bigrams in order of descending rarity
    q_terms.sort(key=lambda term: -idfs[term])
    q_bigrams.sort(key=lambda bigram: -idfs[bigram])
    q_terms.extend(q_bigrams)

    # score and prune results on a term-by-term basis
    results = {}
    enough_results = False
    for term in q_terms:
        postings = search_term(term)
        temp_results = {}
        for posting in postings:
            doc_id = posting.doc_id
            idf = idfs[term]
            score = 0  # weighted sum of tf-idf scores for each important tag
            for tag, tf in posting.tfs.items():
                score += TAG_MULT[tag] * tf * idf
            # intersect if more results than needed, union if less
            if not enough_results or doc_id in results:
                curr_score = results[doc_id] if doc_id in results else 0
                temp_results[doc_id] = curr_score - score
        # can start if required number of results exceeded
        if len(temp_results) > n:
            enough_results = True
        # dont prune too much
        if enough_results and len(temp_results) < n:
            break
        results = temp_results

    # put remaining results in a heap
    results_heap = []
    for doc_id in results:
        results_heap.append((results[doc_id], doc_id))
    heapq.heapify(results_heap)

    # get top n results using heap
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
