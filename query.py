import os
import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_store")
COLLECTION_NAME = "gsu_unofficial_guide"
MODEL_NAME = "all-MiniLM-L6-v2"

# Module-level singletons so the model and DB load once per process
_model = None
_collection = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def retrieve(query: str, k: int = 5) -> list[dict]:
    """Return the top-k most relevant chunks for query, with source and distance."""
    embedding = _get_model().encode([query])[0].tolist()
    results = _get_collection().query(
        query_embeddings=[embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {
            "text": doc,
            "source": meta["source"],
            "chunk_index": meta["chunk_index"],
            "distance": dist,
        }
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]


if __name__ == "__main__":
    # Test retrieval with 3 of the 5 evaluation-plan queries
    test_queries = [
        "What do students say about Dr. Prasad's office hours for OS?",
        "Is the GSU housing lottery actually random?",
        "Which dining hall is open the latest at GSU?",
    ]

    for query in test_queries:
        print(f"\n{'='*64}")
        print(f"QUERY: {query}")
        print("=" * 64)
        for i, r in enumerate(retrieve(query, k=5)):
            print(f"\n  [#{i+1}] source={r['source']}  distance={r['distance']:.4f}")
            print(f"  {r['text'][:350]}")
