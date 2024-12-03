from search import retrieve
from search.app import app
import time
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ui", action="store_true", help="Launch Web UI")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("-p", "--port", default=8000)
    parser.add_argument("--debug", default=True)
    args = parser.parse_args()
    if args.ui:
        print(args)
        app.run(debug=args.debug, host=args.host, port=args.port)
    else:
        query = input("Search:")
        start = time.time()
        results = retrieve(query,5)
        end = time.time()
        for i,result in enumerate(results):
            print(f"{i+1}. {result}")
        print(f"Time elapsed: {end-start}s")
