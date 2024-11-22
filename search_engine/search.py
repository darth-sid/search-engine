from search import retrieve
import time

if __name__ == "__main__":
    query = input("Search:")
    start = time.time()
    results = retrieve(query,5)
    end = time.time()
    for i,result in enumerate(results):
        print(f"{i+1}. {result}")
    print(f"Time elapsed: {end-start}s")
