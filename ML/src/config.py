"""
This module provides configs for the project.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

RAW_311_FILENAME = "311_Service_Requests_from_2020_to_Present_20260321.csv"
PROCESSED_311_FILENAME = "cleaned_311.csv"

RAW_311_PATH = RAW_DIR / RAW_311_FILENAME
PROCESSED_311_PATH = PROCESSED_DIR / PROCESSED_311_FILENAME

MAX_CLEAN_ROWS = 1000000

SOURCE_COLUMNS = [
    "Created Date",
    "Problem (formerly Complaint Type)",
    "Problem Detail (formerly Descriptor)",
    "Longitude",
    "Latitude",
]

RENAMED_COLUMNS = {
    "Problem (formerly Complaint Type)": "Problem",
    "Problem Detail (formerly Descriptor)": "Problem Detail",
}

OUTPUT_COLUMNS = [
    "Created Date",
    "Problem",
    "Problem Detail",
    "Longitude",
    "Latitude",
]
