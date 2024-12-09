from flask import Flask, request
from flask_cors import CORS
from .util import retrieve
import sys

app = Flask(__name__)
c = CORS(app)


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query")
    n = request.args.get("n")
    if query is None:
        return "Specify a query", 400
    if n is None:
        n = 5
    urls = retrieve(query, 10, timed=True)
    return {"time": urls[1], "urls": urls[0]}, 200


if __name__ == "__main__":
    try:
        app.run(debug=True, host="127.0.0.1", port=8000)
    except ModuleNotFoundError:
        print(sys.executable)
