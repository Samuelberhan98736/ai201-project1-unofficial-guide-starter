# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

The domain is **student survival knowledge for CS majors at Georgia State University (GSU)** — covering professor and course reviews, campus resources, housing, dining, and career advice. This knowledge is valuable because it represents what students actually learn through experience: which professors give partial credit, which dorms are loud, which clubs help with recruiting, and how to navigate the course registration system. None of this appears in official GSU publications. Official channels (course catalogs, housing websites, career services pages) give procedural information but never tell you that OS and Algorithms in the same semester will ruin your life, or that the library 4th floor is the only place on campus to get real work done.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors — CS 1301 | Student reviews of CS 1301 professors (Dr. Zhu and Dr. Branagan), grading breakdowns, exam tips | documents/rmp_cs1301_reviews.txt |
| 2 | Rate My Professors — CS 2340 | Student reviews of CS 2340 (Data Structures) professors, assignment expectations | documents/rmp_cs2340_reviews.txt |
| 3 | Rate My Professors — Upper Division | Reviews of CS 4720 (ML), CS 4510 (Networks), CS 3410 (OS) professors | documents/rmp_upper_division_reviews.txt |
| 4 | Rate My Professors — CS 3410 & 4320 | Detailed reviews of OS and Algorithms courses, exam formats, project timelines | documents/rmp_cs3410_cs4320_reviews.txt |
| 5 | Reddit r/GeorgiaStateUniversity — CS Tips | Threads on CS major advice, tutoring resources, research opportunities, recruiting | documents/reddit_gsu_cs_tips.txt |
| 6 | Reddit r/GeorgiaStateUniversity — Housing | Dorm reviews, off-campus housing advice, housing lottery mechanics | documents/reddit_gsu_housing.txt |
| 7 | Reddit r/GeorgiaStateUniversity — Dining | Dining hall rankings, late-night food options, meal plan math | documents/reddit_gsu_dining.txt |
| 8 | Reddit / CS Discord — Internships & Careers | Internship timelines, salary data, recruiting clubs, job search strategy | documents/reddit_gsu_cs_internships.txt |
| 9 | GSU Student Discord — Freshman Survival Guide | Academic tips, PAWS/iCollege usage, MARTA tips, registration advice | documents/gsu_freshman_survival_guide.txt |
| 10 | GSU Student Discord — Study Spots | Ranked study locations, library hours, hidden campus spaces | documents/gsu_study_spots.txt |
| 11 | GSU Student Discord — Campus Resources | Financial aid tips, free software, health services, emergency funds | documents/gsu_campus_resources.txt |
| 12 | GSU CS Discord — Course Planning Guide | Full CS major sequence, concentration tracks, high-demand course tips | documents/gsu_cs_course_planning.txt |

---

## Chunking Strategy

**Chunk size:** 500 characters with 100-character overlap

**Overlap:** 100 characters

**Reasoning:** The documents are a mix of short review snippets (1–4 sentences each) and longer structured guides (multi-paragraph sections). A 500-character chunk is large enough to contain a complete review or a complete piece of advice with its context, but small enough to match specific questions. For example, a review about exam grading should fit in a single chunk rather than spanning two. The 100-character overlap preserves continuity when a key fact falls near a chunk boundary — for instance, a professor's name mentioned at the end of one chunk will appear again at the start of the next, keeping context intact. At 500 characters, the expected chunk count across 12 documents is roughly 200–400 chunks, which is in a healthy range for retrieval quality.

---

## Retrieval Approach

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers` — runs locally with no API key, no rate limits, and produces 384-dimensional embeddings. Good balance of speed and accuracy for English-language opinion and review text.

**Top-k:** 5 chunks per query. This gives the LLM enough context for multi-faceted questions (e.g., "what do students say about Dr. Prasad") without diluting the context with loosely related material.

**Production tradeoff reflection:** For a real deployment I would consider `text-embedding-3-small` from OpenAI or a larger sentence-transformers model like `all-mpnet-base-v2`. The tradeoffs: `all-MiniLM-L6-v2` is fast and free but has a 256-token context limit, which means long review sections may get truncated at embedding time. A larger model like `all-mpnet-base-v2` handles longer inputs better but is ~3x slower to embed. For multilingual support (e.g., if the corpus included Spanish-language reviews), a multilingual model like `paraphrase-multilingual-MiniLM-L12-v2` would be necessary. For production with API-hosted embeddings, cost scales linearly with corpus size — for a 400-chunk corpus this project's size is negligible, but at 100k+ chunks you'd want to cache embeddings aggressively.

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about Dr. Prasad's office hours for OS? | Students strongly recommend going to his office hours; he will trace through memory errors in gdb with you. Multiple reviews specifically say "go to office hours" repeatedly. |
| 2 | Is the GSU housing lottery actually random? | No — it is deposit-date dependent. Students who deposit earliest get the first selection windows. It is not a random lottery. |
| 3 | Which dining hall is open the latest at GSU? | The Hub closes at 10pm weekdays and 9pm weekends. The Market in the library stays open until midnight. |
| 4 | What GPA do you need to keep the HOPE Scholarship? | A 3.0 GPA, recalculated every 30 credit hours. It can be reinstated if you bring your GPA back above 3.0 at the next checkpoint. |
| 5 | What is the grading breakdown for CS 4320 with Dr. Aluru? | Homework 30%, Midterm 35%, Final 35%. He adjusts the grade scale rather than curving the class average. |

---

## Anticipated Challenges

1. **Cross-document retrieval for compound questions:** Some questions require pulling information from multiple documents (e.g., "what's the best way to prepare for upper-division CS at GSU?" spans course planning, professor reviews, and study spots). A single top-k retrieval may not surface all the relevant pieces, leading to partial or incomplete answers.

2. **Informal language and abbreviations:** Student-written reviews use abbreviations (RMP, PAWS, iCollege, MARTA) and informal phrasing that may not match more formal query wording. The embedding model should handle semantic similarity reasonably well, but highly domain-specific terms could cause retrieval misses if the query uses different vocabulary.

---

## Architecture

```
┌─────────────────────┐
│  Raw .txt Documents │  (12 files in documents/)
│  (student reviews,  │
│   Reddit threads,   │
│   Discord guides)   │
└────────┬────────────┘
         │  load + clean text
         ▼
┌─────────────────────┐
│   Ingestion Script  │  Python: read files, strip extra whitespace
│   (ingest.py)       │  and formatting artifacts
└────────┬────────────┘
         │  cleaned text per document
         ▼
┌─────────────────────┐
│   Chunking          │  sentence-transformers CharacterTextSplitter
│   chunk_size=500    │  or manual sliding window
│   overlap=100       │  → list of (chunk_text, source_filename, chunk_index)
└────────┬────────────┘
         │  chunks + metadata
         ▼
┌────────────────────────────────┐
│  Embedding + Vector Store      │  sentence-transformers: all-MiniLM-L6-v2
│  (embed.py)                    │  ChromaDB: local persistent store
│                                │  metadata: {source, chunk_index}
└────────┬───────────────────────┘
         │  vector index on disk
         ▼
┌─────────────────────┐
│   Retrieval         │  query → embed query → ChromaDB similarity search
│   (query.py)        │  top-k=5 → returns chunks + source metadata
└────────┬────────────┘
         │  retrieved chunks + sources
         ▼
┌─────────────────────┐
│   Generation        │  Groq: llama-3.3-70b-versatile
│   (query.py)        │  System prompt enforces grounding:
│                     │  answer only from provided context
│                     │  Response includes source attribution
└────────┬────────────┘
         │  answer + sources
         ▼
┌─────────────────────┐
│   Gradio Web UI     │  app.py
│   (app.py)          │  Input: question textbox
│                     │  Output: answer + "Retrieved from" list
└─────────────────────┘
```

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**
I'll give Claude my Documents section (12 .txt files with review and guide content) and my Chunking Strategy section (500 chars, 100 overlap). I'll ask it to implement `ingest.py` that reads all files from `documents/`, cleans whitespace and formatting artifacts, and outputs a list of dicts with keys `text`, `source`, and `chunk_index`. I'll verify the output by printing 5 chunks and checking they are substantive and self-contained.

**Milestone 4 — Embedding and retrieval:**
I'll give Claude the Architecture diagram and ask it to implement `embed.py` that takes the chunk list from `ingest.py`, embeds each chunk with `SentenceTransformer("all-MiniLM-L6-v2")`, and stores them in a ChromaDB collection with source metadata. Then a `retrieve(query, k=5)` function in `query.py`. I'll verify by running the 5 evaluation plan queries and checking that returned chunks are topically relevant.

**Milestone 5 — Generation and interface:**
I'll give Claude the grounding requirement ("answer only from provided context, cite sources") and the Gradio skeleton from the project spec. I'll ask it to implement the full `ask(question)` function and `app.py`. I'll check that the system prompt actually enforces grounding (not just suggests it) and that source attribution is appended programmatically, not left to the LLM.
