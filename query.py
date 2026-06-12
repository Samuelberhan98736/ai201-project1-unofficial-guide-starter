import os
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_store")
COLLECTION_NAME = "gsu_unofficial_guide"
MODEL_NAME = "all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.3-70b-versatile"

# Module-level singletons so the model and DB load once per process
_model = None
_collection = None
_groq = None


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


def _get_groq():
    global _groq
    if _groq is None:
        _groq = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _groq


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


SYSTEM_PROMPT = """\
You are a helpful assistant for Georgia State University students. \
Answer the user's question using ONLY the information provided in the context documents below. \
Do not use any outside knowledge or make assumptions beyond what is stated in the context. \
If the context does not contain enough information to answer the question, respond with exactly: \
"I don't have enough information in my documents to answer that."

Always end your response with a "Sources:" line that lists every document filename you drew from, \
one per line, formatted as:
Sources:
- <filename>
"""


def ask(question: str, k: int = 9) -> dict:
    """
    Retrieve relevant chunks for question, then generate a grounded answer.
    Returns {"answer": str, "sources": list[str], "chunks": list[dict]}.
    """
    chunks = retrieve(question, k=k)

    # Build context block with source labels so the model can cite them
    context_parts = []
    for c in chunks:
        context_parts.append(f"[Source: {c['source']}]\n{c['text']}")
    context = "\n\n---\n\n".join(context_parts)

    user_message = f"Context documents:\n\n{context}\n\nQuestion: {question}"

    response = _get_groq().chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )

    answer_text = response.choices[0].message.content.strip()

    # Extract source filenames programmatically as a fallback guarantee
    cited_sources = list(dict.fromkeys(c["source"] for c in chunks))

    return {
        "answer": answer_text,
        "sources": cited_sources,
        "chunks": chunks,
    }


if __name__ == "__main__":
    test_queries = [
        "What do students say about Dr. Prasad's office hours for OS?",
        "Is the GSU housing lottery actually random?",
        "Which dining hall is open the latest at GSU?",
        # Out-of-scope query — system should decline
        "What is the best restaurant in downtown Chicago?",
    ]

    for question in test_queries:
        print(f"\n{'='*64}")
        print(f"Q: {question}")
        print("=" * 64)
        result = ask(question)
        print(result["answer"])
