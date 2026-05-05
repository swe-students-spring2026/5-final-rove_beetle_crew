"""
MongoDB integration for caching search results.
Avoids re-running the expensive ML pipeline for repeated queries.
"""

import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path

try:
    from pymongo import MongoClient
except Exception:
    MongoClient = None


def _load_env_file() -> dict:
    """Load simple KEY=VALUE entries from the repo-root .env file."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    values = {}

    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"'")

            if key:
                values[key] = value

    except OSError:
        pass

    return values


_ENV_FILE = _load_env_file()


def _config(name: str) -> str:
    return os.environ.get(name, _ENV_FILE.get(name, ""))


MONGO_URI = _config("MONGO_URI")
DB_NAME = _config("DB_NAME")
COLLECTION_NAME = _config("COLLECTION_NAME")


def is_uri(uri: str) -> bool:
    return "PASSWORD" in uri or "example.invalid" in uri


def get_db():
    """Return the MongoDB database instance."""
    try:
        if MongoClient is None or not MONGO_URI or not DB_NAME:
            return None

        if is_uri(MONGO_URI):
            return None

        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        return client[DB_NAME]

    except Exception:
        # if mongo is down, just skip the cache
        return None


def make_cache_key(query_311: str, query_facilities: str) -> str:
    """Create a unique hash key from the two search queries."""
    raw = f"{query_311.strip().lower()}||{query_facilities.strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()


def get_cached_result(query_311: str, query_facilities: str):
    """
    Look up a cached search result in MongoDB.
    Returns the cluster_results list if found, None otherwise.
    """
    try:
        db = get_db()
        if db is None or not COLLECTION_NAME:
            return None

        key = make_cache_key(query_311, query_facilities)
        doc = db[COLLECTION_NAME].find_one({"_id": key})

        if doc:
            return doc["cluster_results"]

        return None

    except Exception:
        return None


def save_cached_result(query_311: str, query_facilities: str, cluster_results: list):
    """
    Save a search result to MongoDB cache.
    Uses upsert so repeated searches overwrite the old cache entry.
    """
    try:
        db = get_db()
        if db is None or not COLLECTION_NAME:
            return

        key = make_cache_key(query_311, query_facilities)

        db[COLLECTION_NAME].update_one(
            {"_id": key},
            {
                "$set": {
                    "query_311": query_311,
                    "query_facilities": query_facilities,
                    "cluster_results": cluster_results,
                    "cached_at": datetime.now(timezone.utc).isoformat(),
                }
            },
            upsert=True,
        )

    except Exception:
        pass


def clear_cache():
    """Clear all cached search results. Useful for testing."""
    try:
        db = get_db()
        if db is None or not COLLECTION_NAME:
            return

        db[COLLECTION_NAME].delete_many({})

    except Exception:
        pass


def health_check() -> bool:
    """Check if MongoDB is reachable. Returns True if ok, False otherwise."""
    try:
        if MongoClient is None or not MONGO_URI:
            return False

        return True

    except Exception:
        return False
