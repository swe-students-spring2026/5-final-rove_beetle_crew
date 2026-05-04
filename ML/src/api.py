from flask import Flask, jsonify, request

from filter import filter_clusters

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    query_311 = (data.get("query_311") or "").strip()
    query_facilities = (data.get("query_facilities") or "").strip()

    if not query_311 or not query_facilities:
        return jsonify({"error": "Both query_311 and query_facilities are required"}), 400

    clusters = filter_clusters(query_311, query_facilities)

    result = []
    for cluster in clusters:
        facilities = []
        for facility in cluster.facilities:
            facilities.append({
                "name": facility[0] if len(facility) > 0 else "Unknown",
                "group": facility[1] if len(facility) > 1 else "Unknown",
                "subgroup": facility[2] if len(facility) > 2 else "Unknown",
                "type": facility[3] if len(facility) > 3 else "Unknown",
                "borough": facility[4] if len(facility) > 4 else "Unknown",
            })

        total = cluster.total_complaint
        matched = cluster.matched_complaint
        complaint_ratio = matched / total if total > 0 else 0

        result.append({
            "longitude": cluster.center[0],
            "latitude": cluster.center[1],
            "matched_complaints": matched,
            "total_complaints": total,
            "complaint_ratio": round(complaint_ratio, 4),
            "facilities": facilities,
        })

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
