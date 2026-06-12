import os
import re

DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "documents")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def load_documents(docs_dir=DOCUMENTS_DIR):
    docs = []
    for filename in sorted(os.listdir(docs_dir)):
        if filename.endswith(".txt"):
            path = os.path.join(docs_dir, filename)
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read()
            docs.append({"filename": filename, "raw": raw})
    return docs


def clean_text(text):
    # Remove horizontal rule separators (lines of dashes)
    text = re.sub(r"^-{3,}\s*$", "", text, flags=re.MULTILINE)
    # Collapse 3+ blank lines into a single blank line
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip trailing whitespace from each line
    lines = [line.rstrip() for line in text.split("\n")]
    return "\n".join(lines).strip()


def chunk_text(text, source, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    chunk_index = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            # Break at a word boundary — find last space before the limit
            boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary
        chunk = text[start:end].strip()
        if len(chunk) >= 50:  # drop fragments too short to carry meaning
            chunks.append({
                "text": chunk,
                "source": source,
                "chunk_index": chunk_index,
            })
            chunk_index += 1
        next_start = end - overlap
        if next_start <= start:
            next_start = start + 1
        # Advance to the next word boundary so chunks don't start mid-word
        space = text.find(" ", next_start)
        if space != -1 and space < next_start + 30:
            next_start = space + 1
        start = next_start
    return chunks


def load_and_chunk_documents(docs_dir=DOCUMENTS_DIR):
    all_chunks = []
    for doc in load_documents(docs_dir):
        cleaned = clean_text(doc["raw"])
        all_chunks.extend(chunk_text(cleaned, doc["filename"]))
    return all_chunks


if __name__ == "__main__":
    chunks = load_and_chunk_documents()
    print(f"Total chunks: {len(chunks)}\n")

    # Sample 5 chunks spread across the corpus
    indices = [0, len(chunks) // 4, len(chunks) // 2, 3 * len(chunks) // 4, len(chunks) - 1]
    print("=" * 60)
    print("5 REPRESENTATIVE CHUNKS")
    print("=" * 60)
    for idx in indices:
        c = chunks[idx]
        print(f"\n[chunk {idx}] source={c['source']}  chunk_index={c['chunk_index']}")
        print(c["text"])
        print("-" * 40)
