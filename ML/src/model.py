from sentence_transformers import SentenceTransformer
from config import EMBEDDINGS_MODEL

model = SentenceTransformer(EMBEDDINGS_MODEL, device="cpu")
