# The Grounded Answer

**Brite Spark 2026 — Problem 1 (AI / RAG)**
A CLI assistant that answers Household Support Program policy questions strictly from a policy manual, cites the exact clause(s) it relied on, and refuses to answer when the manual does not settle the matter.

> Built by **Dakshan Kumar A**. AI assistance (Claude and ChatGPT) was used in an advisory capacity only — see [`AI-USAGE.md`](./AI-USAGE.md). All design decisions and their reasoning are in [`DECISIONS.md`](./DECISIONS.md).

---

## 1. What this is

Calder County's Household Support Program manual is long, internally inconsistent in places, and amended over time. Staff currently rely on one colleague who has "been there a long time" to interpret it correctly. This project is a command-line assistant that:

- Retrieves the relevant clause(s) for a plain-language question using a hybrid BM25 + sentence-embedding retriever.
- Generates an answer **grounded only** in retrieved clause text, with clause-level citations (e.g. `§4.3.2`).
- Refuses to answer, explicitly, when retrieval confidence is too low — rather than guessing.
- Detects and surfaces at least one known internal contradiction in the manual instead of silently picking a side.

## 2. Current status against the floor

| Requirement | Status |
|---|---|
| Grounded answers with clause-level citation | Implemented (`AnswerAgent`, `CitationValidator`) |
| Visible refusal path | Implemented (`AnswerabilityChecker`, `MIN_RETRIEVAL_SCORE`) |
| Own 10-question test set with honest pass/fail | `evaluation/test_cases.json` + `evaluation/run_evaluation.py` |
| Runs from a clean clone using this README alone | See Section 5 |
| Contradiction handled explicitly, both clauses shown | `ContradictionAgent` (§4.3.2 vs §9.1.4) |
| **Day-2 change (Amendment No. 2026-01) integrated into retrieval/answer logic** | **Not yet integrated.** The amendment text is in the repo and has been read, but the pipeline does not currently ask for or reason about a claim date, and still parses only `data/policy-manual.md`. This is a known, logged gap — see `DECISIONS.md`, Decision 6. |

Do not assume the assistant currently gives date-correct answers for anything after 1 March 2026 — it does not yet.

## 3. Architecture

```
Question
   │
   ▼
RetrievalAgent  ──► detects an explicit §citation in the question (if any)
   │                and forces it into the evidence set
   ▼
HybridRetriever ──► BM25Retriever (lexical) + SemanticRetriever (embeddings)
   │                scores combined 30% BM25 / 70% semantic
   ▼
AnswerabilityChecker ──► refuses (NEEDS_COUNTY_INSIGHT) if top score < MIN_RETRIEVAL_SCORE
   │
   ▼
ContradictionAgent ──► short-circuits to a conflict message if the known
   │                    §4.3.2 / §9.1.4 conflict is in the evidence set
   ▼
AnswerAgent ──► builds a strict, no-outside-knowledge prompt, calls Groq,
   │            parses a Status line, strips it, extracts + validates citations
   ▼
CLI output: Status / Answer / (County Insight) / Citations
```

### Repository layout

```
.
├── data/
│   └── policy-manual.md          # the corpus (source of truth)
├   └─ Amendment No. 2026-01.md   # Day-2 change
├── src/
│   ├── config.py                 # paths, model name, TOP_K, MIN_RETRIEVAL_SCORE
│   ├── main.py                   # CLI entry point (Click)
│   ├── ingestion/
│   │   └── parser.py             # markdown → Clause objects, keyed by §citation
│   ├── retrieval/
│   │   ├── bm25_retriever.py
│   │   ├── semantic_retriever.py
│   │   └── hybrid_retriever.py
│   ├── validation/
│   │   ├── answerability.py      # refusal threshold logic
│   │   └── citation_validator.py # drops any citation not actually retrieved
│   ├── agents/
│   │   ├── retrieval_agent.py
│   │   ├── evidence_agent.py
│   │   ├── contradiction_agent.py
│   │   └── answer_agent.py
│   ├── llm/
│   │   ├── client.py             # Groq client + anti-hallucination system prompt
│   │   └── prompts.py
│   ├── models/
│   │   └── schemas.py            # Clause, RetrievedClause, AnswerResult
│   └── utils/
│       └── logger.py
├── evaluation/
│   ├── test_cases.json           # the 10-question test set
│   └── run_evaluation.py
├── tests/
│   ├── test_parser.py
│   ├── test_retrieval.py
│   └── test_decisions.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## 4. Prerequisites

- **Python 3.10 or newer** (3.11 recommended).
- **pip**.
- **Internet access on first run.** Two things get downloaded automatically the first time you run the app or the tests:
  - The `all-MiniLM-L6-v2` embedding model from Hugging Face (~90 MB).
  - `torch`, a transitive dependency of `sentence-transformers` (several hundred MB, largest single install in this project). This is deliberate — see `DECISIONS.md`, Decision 2 — but it means the very first run will be slower and needs network access. Subsequent runs use the local Hugging Face cache and work offline.
- A **free Groq API key** (used for answer generation). Get one at [console.groq.com](https://console.groq.com/).

## 5. Setup (clean clone → running assistant)

```bash
# 1. Clone
git clone <this-repo-url>
cd <repo-folder>

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key
cp .env.example .env
# open .env and set:
#   GROQ_API_KEY=your_actual_key_here

# 5. Run the assistant
python -m src.main
```

You should see:

```
Loading policy manual...
Calder County Policy Assistant started!
Type 'quit' to exit.

You:
```

Ask something like: `How many days does a recipient have to report a change of circumstances?` — this question is expected to trigger the **conflict** path (§4.3.2 vs §9.1.4).

Type `quit` to exit.

### Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `ValueError: GROQ_API_KEY is missing.` | `.env` wasn't created or the key wasn't filled in. Re-check step 4. |
| First run hangs / is very slow | Expected — it's downloading the embedding model and `torch`. Let it finish once; it's cached after that. |
| `ModuleNotFoundError` for any package | Confirm the virtual environment is activated and `pip install -r requirements.txt` completed without errors. |
| Answers look ungrounded or invent facts | Check `MIN_RETRIEVAL_SCORE` in `src/config.py` — this is the refusal threshold, not a bug per se; see Decision 3 in `DECISIONS.md`. |

## 6. Running the tests

```bash
pytest
```

This runs `tests/test_parser.py`, `tests/test_retrieval.py`, and `tests/test_decisions.py`, which check that the manual parses into clauses, that a known clause (`4.3.2`) exists, and that BM25, semantic, and hybrid retrieval all return results for a sample query.

## 7. Running the evaluation suite

```bash
python evaluation/run_evaluation.py
```

This runs the 10 hand-written questions in `evaluation/test_cases.json` against the retrieval + refusal + contradiction logic (it does not call the LLM, so it runs without a Groq key) and prints a PASS/FAIL line per question plus a final score. The test set is intentionally not all-passing-by-design — it includes questions the system is expected to refuse and one it is expected to flag as a conflict, per the hackathon's own guidance not to submit only easy questions.

## 8. Configuration reference (`src/config.py`)

| Setting | Default | What it controls |
|---|---|---|
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence-transformers model used for semantic retrieval |
| `TOP_K` | `5` | Number of clauses retrieved per query |
| `MIN_RETRIEVAL_SCORE` | `0.40` | Refusal threshold — below this, the system declines rather than guesses |

## 9. Known limitations (read before judging)

- **Amendment No. 2026-01 is not yet applied.** The pipeline has no concept of "claim date" and always answers as if the December 2025 consolidated manual is current. A question about a claim dated after 1 March 2026 will currently get an answer based on stale figures (e.g. the old $120 earnings disregard, the old 10-day reporting window). This is logged and being worked on — see `DECISIONS.md`, Decision 6.
- **Contradiction detection is hand-coded to one known pair of clauses** (`§4.3.2` / `§9.1.4`), not a general contradiction detector. This was a deliberate scope decision for the hackathon timeline — see Decision 4.
- An unresolved conflict between two hackathon documents on permitted AI-tool usage was identified early and sent to `hackathon@britesys.com` for clarification; see Decision 5 and `DECISIONS.md` for the question as logged.

## 10. Corpus and citation policy

`data/policy-manual.md` is the sole authority the assistant is allowed to draw on for policy content. The system prompt in `src/llm/prompts.py` explicitly forbids outside knowledge, invented exceptions, and turning `AND` into `OR` (or vice versa) from the source text. Every citation printed by the CLI has been checked against the clauses actually retrieved for that question (`CitationValidator`) before being shown to the user.
