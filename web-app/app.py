import os

import requests
from flask import Flask, render_template, request

app = Flask(__name__)

ML_API_URL = os.environ.get("ML_API_URL", "http://localhost:8000")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    query_311 = request.form.get("query_311", "").strip()
    query_facilities = request.form.get("query_facilities", "").strip()

    if not query_311 or not query_facilities:
        error = "Must enter both a complaint and facility type."
        return render_template("index.html", error=error)

    try:
        response = requests.post(
            f"{ML_API_URL}/recommend",
            json={"query_311": query_311, "query_facilities": query_facilities},
            timeout=120,
        )
        response.raise_for_status()
        cluster_results = response.json()

        return render_template(
            "results.html",
            query_311=query_311,
            query_facilities=query_facilities,
            clusters=cluster_results,
        )
    except Exception as e:
        error = f"Something went wrong while processing your search: {e}"
        return render_template("index.html", error=error)


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
