from sentence_transformers import SentenceTransformer

# Loads model locally — no API call, no network needed
# Downloads once, cached forever after
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str) -> list[float]:
    """
    Convert text → vector embedding locally.
    Returns list of 384 floats.
    Note: sync function — sentence-transformers is not async
    """
    embedding = model.encode(text)
    return embedding.tolist()


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Batch embed multiple texts — efficient single model call.
    """
    embeddings = model.encode(texts)
    return embeddings.tolist()
