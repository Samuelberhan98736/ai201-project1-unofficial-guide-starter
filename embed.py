import os
import chromadb
from sentence_transformers import SentenceTransformer
from ingest import load_and_chunk_documents

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_store")
COLLECTION_NAME = "gsu_unofficial_guide"
MODEL_NAME = "all-MiniLM-L6-v2"


def build_vector_store():
    print("Loading and chunking documents...")
    chunks = load_and_chunk_documents()
    print(f"  {len(chunks)} chunks ready")

    print(f"Loading embedding model ({MODEL_NAME})...")
    model = SentenceTransformer(MODEL_NAME)

    print("Embedding chunks...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    print("Storing in ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Drop and recreate so re-runs don't duplicate data
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    collection.add(
        ids=[f"{c['source']}__{c['chunk_index']}" for c in chunks],
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=[{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks],
    )

    print(f"Done — {collection.count()} chunks stored in {CHROMA_DIR}/")
    return collection


if __name__ == "__main__":
    build_vector_store()
