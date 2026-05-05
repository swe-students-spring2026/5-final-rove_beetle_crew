FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# Install CPU-only torch first, then everything else except torch
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    grep -v '^torch$' requirements.txt | pip install --no-cache-dir -r /dev/stdin

# Pre-download the embedding model so it's baked into the image
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device='cpu')"

COPY src/ ./src/
COPY data/ ./data/

WORKDIR /app/src

EXPOSE 8000

CMD ["python", "api.py"]
