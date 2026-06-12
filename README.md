# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

This system covers **student survival knowledge for CS majors at Georgia State University (GSU)** — professor and course reviews, campus housing, dining, career advice, and hidden campus resources. This knowledge is valuable because it represents hard-won experience that students share with each other informally: which professors give partial credit, which dorms are loud, how the housing lottery actually works, and which clubs actually help with recruiting. None of this appears in official GSU publications. The official course catalog describes what a class covers; it does not tell you that CS 3410 and CS 4320 in the same semester will destroy your GPA, or that Dr. Prasad will literally debug gdb crashes with you in office hours.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors — CS 1301 | Professor reviews | documents/rmp_cs1301_reviews.txt |
| 2 | Rate My Professors — CS 2340 | Professor reviews | documents/rmp_cs2340_reviews.txt |
| 3 | Rate My Professors — Upper Division (ML, Networks, OS) | Professor reviews | documents/rmp_upper_division_reviews.txt |
| 4 | Rate My Professors — CS 3410 & CS 4320 | Professor reviews | documents/rmp_cs3410_cs4320_reviews.txt |
| 5 | Reddit r/GeorgiaStateUniversity — CS Tips | Forum thread | documents/reddit_gsu_cs_tips.txt |
| 6 | Reddit r/GeorgiaStateUniversity — Housing | Forum thread | documents/reddit_gsu_housing.txt |
| 7 | Reddit r/GeorgiaStateUniversity — Dining | Forum thread | documents/reddit_gsu_dining.txt |
| 8 | Reddit / CS Discord — Internships & Careers | Forum thread | documents/reddit_gsu_cs_internships.txt |
| 9 | GSU Student Discord — Freshman Survival Guide | Community wiki | documents/gsu_freshman_survival_guide.txt |
| 10 | GSU Student Discord — Study Spots | Community wiki | documents/gsu_study_spots.txt |
| 11 | GSU Student Discord — Campus Resources | Community wiki | documents/gsu_campus_resources.txt |
| 12 | GSU CS Discord — Course Planning Guide | Community wiki | documents/gsu_cs_course_planning.txt |

---

## Chunking Strategy

**Chunk size:** 500 characters

**Overlap:** 100 characters

**Why these choices fit your documents:** The corpus is a mix of short review snippets (1–4 sentences per review) and longer structured guides (multi-paragraph sections). A 500-character chunk is large enough to contain a complete review or a self-contained piece of advice with its surrounding context, but small enough that a specific query can match it precisely. The 100-character overlap preserves continuity at chunk boundaries — if a key fact (like a professor's name) falls at the end of one chunk, it reappears at the start of the next so the embedding of adjacent chunks carries some of the same semantic signal. Before chunking, the pipeline strips horizontal rule separators (`---`), collapses multiple blank lines into one, and strips trailing whitespace per line. The chunker also breaks at word boundaries (finds the last space before the 500-character limit) and skips fragments shorter than 50 characters.

**Final chunk count:** 118 chunks across 12 documents.

---

## Sample Chunks

**Chunk 4 — source: gsu_campus_resources.txt**
```
tools for free. Log in at software.gsu.edu with your student credentials. This is a huge benefit
most students don't use.

Computer labs: The CS computer lab in Classroom South has Linux workstations that are required
for certain CS assignments (especially OS and Systems courses). Hours are posted on the CS
department website. During finals, labs are open extended hours.

Virtual Private Network (VPN): GSU provides a free VPN for students to access campus resources
remotely. Install it before
```

**Chunk 22 — source: gsu_freshman_survival_guide.txt**
```
Source: GSU unofficial freshman survival guide — compiled from orientation Discord and class
Facebook groups. Collected from: Multiple GSU student community posts

ACADEMIC SURVIVAL

iCollege is GSU's learning management system. All your syllabi, assignments, and grades live
here. Download the app. Set up email notifications for announcements — some professors post
assignment changes on iCollege without emailing you separately.

PAWS is the student portal for registration, financial aid, and
```

**Chunk 45 — source: reddit_gsu_cs_internships.txt**
```
a URL shortener)
- January: Received offer for summer internship at Atlanta-area fintech company, $30/hr

What helped most:
1. My GitHub had 4 complete projects including a React/Node full-stack app and a Python data
analysis project with visualizations. The interviewer mentioned my GitHub specifically.
2. I'd solved about 60 LeetCode mediums and 20 hards before the interview. The actual problems
were easier than I expected.
3. The Career Services mock interview was genuinely useful — they told
```

**Chunk 71 — source: reddit_gsu_dining.txt**
```
Five Points food trucks on weekends

For grocery shopping: There's a Publix on Ponce de Leon (20 min walk) and a Kroger further out.
Neither is super convenient without a car. MARTA gets you to a Dekalb Farmers Market on the
east line which has incredible prices if you're cooking for yourself.

Thread title: "Which dining hall is open the latest?"
Posted by: u/night_owl_gsu

The Hub closes at 10pm on weekdays and 9pm on weekends. Piedmont North closes at 9pm weekdays,
8pm weekends. The only
```

**Chunk 100 — source: rmp_cs3410_cs4320_reviews.txt**
```
Projects 50%, Midterm 20%, Final 30%. The projects are hard but educational. Project 1 is a Unix
shell — you implement pipes, redirects, and background processes. Project 2 is a user-level
thread library using setjmp/longjmp (brutal). Project 3 is memory allocation. Each project builds
on the next. Start them the day they're assigned.

Review 3:
His office hours are the most useful on campus for this course. He will literally sit with you
and trace through memory errors in gdb. Go to office
```

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`. This model runs entirely locally — no API key and no rate limits. It produces 384-dimensional embeddings and is well-suited for English-language semantic similarity tasks including short opinion-based text. The ChromaDB collection was created with `hnsw:space: cosine` so that distances reflect cosine similarity (lower = more similar) rather than raw L2 distance.

**Production tradeoff reflection:** For a real deployment I would consider `text-embedding-3-small` from OpenAI or `all-mpnet-base-v2` from sentence-transformers. The key tradeoffs: `all-MiniLM-L6-v2` has a 256-token context limit, which means long review sections can be silently truncated at embedding time — `all-mpnet-base-v2` handles up to 384 tokens and generally produces more accurate embeddings at roughly 3× the latency. For multilingual support (e.g., Spanish-language reviews), a multilingual model like `paraphrase-multilingual-MiniLM-L12-v2` would be required. For API-hosted embeddings at scale, `text-embedding-3-small` costs ~$0.02 per million tokens and is significantly more accurate on domain-specific retrieval tasks, but adds API dependency and per-query cost. For a 118-chunk corpus, any of these models would work; the choice matters more at 100k+ chunks where recall differences compound.

---

## Grounded Generation

**System prompt grounding instruction:**

```
You are a helpful assistant for Georgia State University students.
Answer the user's question using ONLY the information provided in the context documents below.
Do not use any outside knowledge or make assumptions beyond what is stated in the context.
If the context does not contain enough information to answer the question, respond with exactly:
"I don't have enough information in my documents to answer that."

Always end your response with a "Sources:" line that lists every document filename you drew from,
one per line, formatted as:
Sources:
- <filename>
```

The prompt instructs the model to answer *only* from provided context, not to use outside knowledge, and to explicitly refuse rather than speculate when context is insufficient. Temperature is set to 0.2 to reduce hallucination variability.

**How source attribution is surfaced in the response:** The LLM is instructed to list source filenames in every response. Additionally, `ask()` programmatically extracts the unique source filenames from the retrieved chunks and stores them in `result["sources"]`, so source attribution is guaranteed regardless of whether the LLM follows the instruction — the Gradio UI always shows the retrieved-from list from `result["sources"]`.

---

## Retrieval Test Results

**Query 1: "Is the GSU housing lottery actually random?"**

Top returned chunks:
- `reddit_gsu_housing.txt` (distance 0.220) — Contains the thread titled "GSU housing lottery — is it actually random?" and the full Q&A explaining the priority tier system.
- `reddit_gsu_housing.txt` (distance 0.319) — Contains the detailed answer listing all four priority tiers and the explanation that it is deposit-date dependent.
- `reddit_gsu_housing.txt` (distance 0.397) — Contains the follow-up answer: "Applications for fall usually open in February. Students who deposit in February get first pick."

**Why these chunks are relevant:** The query uses the exact phrase "housing lottery" and "actually random," which matches the thread title directly. The top three results are all from the same source file and each contains a sequential part of the answer. This is the clearest example of retrieval working correctly — the embedding model surfaces the right document and the right section within it.

---

**Query 2: "Which dining hall is open the latest at GSU?"**

Top returned chunks:
- `reddit_gsu_dining.txt` (distance 0.302) — Contains the dining hall rankings intro including Hub closing time.
- `gsu_study_spots.txt` (distance 0.481) — Related to campus spaces but not directly about dining hours.
- `reddit_gsu_dining.txt` (distance 0.543) — Contains the thread "Which dining hall is open the latest?" with exact closing times: Hub 10pm weekdays, Piedmont North 9pm, The Market midnight.

**Why the relevant chunk is relevant:** Chunk 7 of `reddit_gsu_dining.txt` contains the direct answer because the thread title in the source document closely matches the query. The distance of 0.543 is higher than ideal — this chunk ranks 7th rather than 1st — because the query phrase "open the latest" doesn't share exact vocabulary with "closes at 10pm." Semantic similarity alone bridges this gap, but not as strongly as for the housing lottery query where the phrasing was nearly identical.

---

**Query 3: "What GPA do you need to keep the HOPE Scholarship?"**

Top returned chunks:
- `gsu_campus_resources.txt` (distance 0.399) — Contains the HOPE Scholarship section: "maintain a 3.0 GPA... recalculates every 30 credit hours... can be reinstated."
- `gsu_freshman_survival_guide.txt` (distance 0.606) — Contains mentions of GPA and academic standing generally.
- `reddit_gsu_cs_tips.txt` (distance 0.609) — Off-topic; returned due to loose GPA/academic keyword match.

**Why the top chunk is relevant:** The top-ranked chunk contains the HOPE Scholarship section almost verbatim. The query terms "GPA," "keep," and "HOPE Scholarship" all appear in this chunk, resulting in a strong semantic match (distance 0.399). Results 2–9 are less relevant — they mention GPA in different contexts — but the LLM correctly draws only from the high-relevance top chunk in its answer.

---

## Grounded Generation Examples

**Example 1 — Well-grounded response with source attribution:**

> **Query:** Is the GSU housing lottery actually random?
>
> **Response:** The GSU housing lottery is not a pure lottery. Priority tiers are: (1) students with medical/disability accommodations, (2) first-year students who deposit early — earlier deposits get earlier selection windows, (3) returning residents, (4) everyone else in selection order based on deposit date. Athletes live in their own facility and do not get priority in the general pool, and honors students do not get separate priority.
>
> Sources:
> - reddit_gsu_housing.txt

---

**Example 2 — Grounded response with partial source list:**

> **Query:** What GPA do you need to keep the HOPE Scholarship?
>
> **Response:** To keep the HOPE Scholarship, you need to maintain a 3.0 GPA. If you drop below 3.0, you lose the scholarship, but if you bring it back up above 3.0 at the next checkpoint, it can be reinstated.
>
> Sources:
> - gsu_campus_resources.txt

---

**Example 3 — Out-of-scope query correctly refused:**

> **Query:** What is the best restaurant in downtown Chicago?
>
> **Response:** I don't have enough information in my documents to answer that.
>
> Sources:
> - reddit_gsu_dining.txt

The system retrieved the dining file (it's the closest topic match) but correctly declined to answer rather than generating a plausible-sounding response from the model's general knowledge about Chicago restaurants.

---

## Query Interface

**Input field:** A multi-line textbox labeled "Your question." Supports pressing Enter to submit or clicking the "Ask" button. Six pre-loaded example queries are available at the bottom of the page to demonstrate the system without typing.

**Output fields:** Two side-by-side panels — "Answer" (10 lines, shows the LLM-generated grounded response) and "Retrieved from" (10 lines, shows the source document filenames the answer drew from).

**To run:** With the virtual environment activated, run `python app.py`. The interface launches at `http://localhost:7860`.

**Sample interaction transcript:**

```
Input:  Which dining hall is open the latest at GSU?

Answer: The Hub is open until 10pm on weekdays. However, it's not the only option
        for late-night food, as The Market in the library is open until midnight.
        Among the traditional dining halls, The Hub is the one that stays open
        the latest.

        Sources:
        - reddit_gsu_dining.txt

Retrieved from:
  • reddit_gsu_dining.txt
  • gsu_study_spots.txt
  • reddit_gsu_housing.txt
  • gsu_freshman_survival_guide.txt
```

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Dr. Prasad's office hours for OS? | Multiple reviews say his office hours are the best on campus; he will trace through gdb errors with you in person | "Students do not explicitly mention Dr. Prasad's office hours. Dr. Cai's office hours were unhelpful." | Partially relevant — the key chunk is retrieved (dist 0.578) but doesn't contain the professor's name | Inaccurate |
| 2 | Is the GSU housing lottery actually random? | No — it is deposit-date dependent; earlier depositors get earlier selection windows | Correctly explains the four priority tiers and confirms it is deposit-date dependent, not random | Relevant — top 3 results all from the housing file, distances 0.22–0.40 | Accurate |
| 3 | Which dining hall is open the latest at GSU? | The Hub closes at 10pm weekdays; The Market in the library closes at midnight | Correctly identifies The Hub (10pm) and The Market (midnight) | Relevant — dining file retrieved twice in top 9, key hours chunk at dist 0.543 | Accurate |
| 4 | What GPA do you need to keep the HOPE Scholarship? | 3.0 GPA, recalculated every 30 credit hours, can be reinstated | Correctly states 3.0 GPA and the reinstatement rule | Relevant — top result from gsu_campus_resources.txt at dist 0.399 | Accurate |
| 5 | What is the grading breakdown for CS 4320 with Dr. Aluru? | Homework 30%, Midterm 35%, Final 35%; he adjusts grade scale rather than curving | "I don't have enough information in my documents to answer that." | Off-target — retrieved CS 2340 and CS 1301 grading chunks instead of the Aluru section | Inaccurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** "What do students say about Dr. Prasad's office hours for OS?"

**What the system returned:** The system said students do not explicitly mention Dr. Prasad's office hours, and instead described Dr. Cai's office hours as unhelpful.

**Root cause (tied to a specific pipeline stage):** This is a chunking stage failure caused by a professor-name/content split at a chunk boundary. In `rmp_cs3410_cs4320_reviews.txt`, the section reads:

```
Professor: Dr. Sushil Prasad
Course: CS 3410 — Operating Systems
...
Review 3:
His office hours are the most useful on campus for this course. He will literally
sit with you and trace through memory errors in gdb. Go to office hours. Go to
office hours. Go to office hours.
```

The character-based chunker (500 chars, 100 overlap) placed the professor's name in one chunk and the office hours praise in a later chunk. The office hours chunk begins with "His office hours are the most useful..." — the pronoun "He" without "Dr. Prasad." When the LLM sees this chunk alongside a chunk about Dr. Cai's (unhelpful) office hours, it cannot confidently attribute the "He will literally sit with you" praise to Dr. Prasad. It correctly refuses to guess rather than attribute the quote to the wrong professor, but the result is an inaccurate "no information" response when the information is present.

**What you would change to fix it:** Use paragraph-aware chunking so that a professor section (name header + all reviews) stays together as a unit. Alternatively, inject document-level metadata into each chunk text at ingestion time — e.g., prefix every chunk from a professor review section with `[Professor: Dr. Sushil Prasad, Course: CS 3410]` — so the name travels with the content regardless of where the chunk boundary falls.

---

## Spec Reflection

**One way the spec helped you during implementation:**

The chunking strategy section of `planning.md` required me to state an explicit chunk size (500 characters) and overlap (100 characters) and explain why those numbers fit the documents *before* writing any code. This meant I had already thought through the tradeoff between review-sized snippets and longer guide sections before I hit the chunking stage. When I ran the first output and inspected 5 sample chunks, I had a clear mental benchmark for what "good" looked like — I could immediately see that chunks breaking mid-word were wrong and fix the word-boundary logic, rather than having to figure out the quality bar from scratch.

**One way your implementation diverged from the spec, and why:**

The spec specified top-k = 5 for retrieval. During testing in Milestone 4 and 5, I discovered that the relevant chunks for two of the five evaluation queries (dining hall hours and Dr. Prasad) were ranked 6th or 7th rather than in the top 5. I increased k to 9 after inspecting the distance scores and confirming that the relevant chunks were present in the corpus but just outside the k=5 window. This fixed the dining hall query but not the Dr. Prasad query (which is a chunking problem, not a k problem). The spec was updated after this change to reflect k=9.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The Architecture section from `planning.md` (the ASCII pipeline diagram labeling each stage with its tool), the Chunking Strategy section (500 chars, 100 overlap, word-boundary splitting), and the Documents section (12 .txt files with review and guide content). I asked Claude to implement `ingest.py` that loads all `.txt` files from `documents/`, cleans whitespace artifacts, and produces a list of dicts with keys `text`, `source`, and `chunk_index`.
- *What it produced:* A working `ingest.py` with `load_documents()`, `clean_text()`, and `chunk_text()` functions. The initial version used fixed-character splitting without word-boundary awareness, causing chunks to start mid-word.
- *What I changed or overrode:* I identified the mid-word start problem by inspecting the 5 sample chunks and directed the AI to fix it by (1) breaking at the last space before the chunk size limit and (2) advancing the next start position to the next word boundary after the overlap offset. I also added a minimum chunk length of 50 characters to filter out fragments.

**Instance 2**

- *What I gave the AI:* The Architecture diagram and the Retrieval Approach section from `planning.md`. I asked Claude to implement `embed.py` (embed all chunks with `all-MiniLM-L6-v2` and store in ChromaDB with source metadata) and `query.py` (`retrieve()` function returning top-k chunks with distance scores).
- *What it produced:* Working `embed.py` and `query.py` using ChromaDB's default L2 distance metric.
- *What I changed or overrode:* After testing retrieval in Milestone 4, I saw that the default L2 distance metric gave inconsistent distance scales compared to the 0–1 cosine range the project spec references. I directed the AI to change the ChromaDB collection to use `hnsw:space: cosine`, then rebuilt the vector store. This improved ranking quality — the housing lottery query dropped from distance 0.44 (L2) to 0.22 (cosine) for its top result, reflecting a more meaningful similarity score.
