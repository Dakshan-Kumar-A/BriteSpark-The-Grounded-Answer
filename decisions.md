# DECISIONS.md

This document records the key technical and architectural decisions made for **The Grounded Answer** project, including the reasoning, trade-offs, and constraints considered.

---

# Decision 1: Technology Stack and Tool Selection

## Context

The goal of this project is to build a policy-question answering assistant that can:

- Answer questions using only the provided policy manual.
- Ground every substantive answer in specific clauses from the manual.
- Provide verifiable clause-level citations.
- Refuse to answer when the manual does not provide sufficient evidence.
- Explicitly surface contradictions when relevant policy clauses conflict.
- Run reliably from a clean clone using the README alone.
- Be developed within the limited time available for the hackathon.

The provided corpus is relatively small, consisting of approximately twenty pages of policy content. Therefore, the main engineering challenge is not large-scale data storage or retrieval performance. The primary challenge is **reliability**: ensuring that the system does not produce a confident answer when the policy manual does not clearly support one.

Based on these constraints, the technology stack was selected to prioritize:

1. Simplicity and rapid implementation.
2. Minimal external infrastructure.
3. Transparent and debuggable retrieval.
4. Separation between retrieval, validation, contradiction detection, and answer generation.
5. Easy reproducibility from a clean clone.
6. Strong support for grounded answers and refusal behavior.

---

## Decision

The project uses the following technology stack:

| Component | Technology | Purpose |
|---|---|---|
| Programming Language | Python 3.11+ | Core application development |
| Policy Corpus | Markdown | Source policy document |
| Document Parsing | Python standard library + Regex | Extract clause-level policy units |
| Lexical Retrieval | `rank-bm25` | Exact and keyword-based retrieval |
| Semantic Retrieval | `sentence-transformers` | Meaning-based retrieval |
| Embedding Model | `all-MiniLM-L6-v2` | Generate local semantic embeddings |
| Vector Operations | NumPy | Cosine similarity and score calculations |
| Retrieval Strategy | Custom Hybrid Retrieval | Combine lexical and semantic retrieval |
| LLM Provider | Groq API | Generate grounded natural-language responses |
| Configuration | `python-dotenv` | Secure environment variable loading |
| CLI | Click | Command-line interaction |
| Testing | Pytest | Unit and integration testing |
| Evaluation | JSON + Python | Ten-question evaluation dataset and result reporting |
| Version Control | Git | Commit history and reproducibility |

No database, external vector database, frontend, orchestration framework, or cloud infrastructure is used.

---

## Why Python Was Chosen

Python was selected because the project requires document processing, information retrieval, embedding generation, evaluation, and integration with an LLM API.

Python provides mature libraries for all of these requirements while allowing the complete system to remain relatively small and easy to understand.

Using a single language also reduces development overhead during a time-limited hackathon. The team does not need to manage separate frontend, backend, database, or infrastructure layers.

Python also allows each stage of the pipeline to be implemented as an independent module:

```text
Policy Manual
     ↓
Parser
     ↓
Retrieval
     ↓
Evidence Validation
     ↓
Contradiction Detection
     ↓
Answer / Refusal Generation

No database, vector store, frontend, or orchestration framework (e.g. LangChain) is used. Retrieval, evidence validation, contradiction detection, and answer generation are kept as separate modules (`retrieval/`, `validation/`, `agents/`) precisely so that any one of them can be changed without rewriting the others — which mattered when the Day 2 amendment landed (see Decision 6).

---

## Decision 2 — Hybrid BM25 + embeddings, accepting the `torch` install cost

### Context

Two options were considered for retrieval:

- **BM25-only.** Lighter, zero risk of a slow or broken install during a judged demo, no `torch` dependency.
- **Hybrid BM25 + sentence-transformer embeddings.** Better recall on paraphrased questions (a caseworker asking "how do I tell the department about changes?" instead of "report a change of circumstances"), at the cost of pulling in `torch` as a transitive dependency of `sentence-transformers` — the single heaviest install in the project, plus a one-time model download from Hugging Face on first run.

### Decision

Went with **hybrid retrieval**, weighted 70% semantic / 30% BM25 (`HybridRetriever`). Pure keyword matching under-serves the actual failure mode this problem is testing for: a caseworker who doesn't know the manual's exact phrasing.

### Mitigation

Because this is a real demo-environment risk, it is called out explicitly rather than left for someone to discover mid-demo:

- Documented as a prerequisite in the README (Section 4) with an explicit "internet access required on first run" note.
- Documented as a possible troubleshooting cause ("first run is slow — this is expected").
- `EMBEDDING_MODEL`, `TOP_K` and the score-blend weights are isolated in `src/config.py` / `HybridRetriever`, so falling back to BM25-only is a small, localized change if the demo environment turns out not to support the `torch` install — it does not require touching the retrieval interface used by the rest of the pipeline.

---

## Decision 3 — Where the answer/refusal line is drawn

### Context

The floor requires "a visible refusal path" that is "calibrated" rather than arbitrary. This is a judgement call with no single right answer, and the reasoning matters more than the specific number chosen.

### Decision

`MIN_RETRIEVAL_SCORE = 0.40` in `src/config.py`, checked against the **top hybrid retrieval score** (`AnswerabilityChecker.can_answer`). Below this, the system returns `NEEDS_COUNTY_INSIGHT` rather than attempting an answer, regardless of what the LLM might otherwise generate.

The threshold sits on the retrieval score rather than on an LLM self-reported confidence, deliberately: an LLM asked "are you sure?" tends to be overconfident, but a low top retrieval score is a comparatively honest signal that nothing in the corpus is actually close to the question — which is exactly the failure mode ("apparent gap" content, and genuinely out-of-scope questions like unemployment insurance) the floor asks us to catch.

The trade-off accepted: a threshold that catches out-of-scope questions reliably will also occasionally refuse a legitimate but obliquely-phrased question. That is treated as the safer failure direction for this domain — a caseworker getting "ask a supervisor" for an answerable question is a minor inconvenience; a caseworker getting a fluent wrong answer is the harm this whole problem is about avoiding.

The LLM is given a **second, independent** chance to decline via the `NEEDS_COUNTY_INSIGHT` / `NOT_FOUND` / `OUT_OF_SCOPE` status vocabulary in the system prompt (`src/llm/prompts.py`), so refusal is not a single point of failure — it happens at both the retrieval-confidence layer and the generation layer.

---

## Decision 4 — Contradiction handling: targeted, not general

### Context

The corpus guarantees at least one genuine internal inconsistency and does not say where it is. On reading, the clearest one is the reporting-deadline conflict: §4.3.2 requires a change of circumstances to be reported within **10 calendar days**, while §9.1.4 refers to a **30 calendar days** reporting period "required under §4.3" for the same obligation. These cannot both be the operative deadline.

### Decision

Built a dedicated `ContradictionAgent` that checks whether both §4.3.2 and §9.1.4 are present in the retrieved evidence set and, if so, short-circuits straight past the LLM to a fixed message surfacing both clauses side by side, rather than letting the LLM silently pick one number.

This was scoped deliberately narrow (checking for one known clause pair) rather than building a general contradiction detector, given the hackathon timeline. A general detector — e.g. flagging any two retrieved clauses whose numeric claims disagree — was considered but rejected as a time sink with a high false-positive rate on a manual this size, when the floor only requires handling contradiction on at least one case.

**Known consequence of Amendment No. 2026-01:** the amendment resolves this exact conflict by setting both figures to 14 days for changes occurring on or after 1 March 2026 (see `Amendment No. 2026-01.md`, §2). That means whether this is still a live contradiction depends on the date of the change being asked about — which the current pipeline does not yet track. Until Decision 6 is implemented, `ContradictionAgent` will keep reporting a conflict even for post-amendment scenarios where the two figures have in fact been aligned. This is called out here rather than quietly left as a bug.

---

## Decision 5 — AI-usage policy conflict, referred rather than assumed

### Context

Two of the hackathon's own documents (the Participant Handbook and the problem/README materials) were read carefully as part of scoping this project, and appeared to give different guidance on the extent of permitted AI tool use during the hackathon.

### Decision

Rather than guessing which document takes precedence, the question was sent to `hackathon@britesys.com` for clarification, and logged here rather than resolved silently:

> **Open question sent to organisers:** where the Participant Handbook and the problem-set AI-usage guidance appear to differ on the scope of permitted AI assistance, which document governs, and does the same answer apply for planning/design assistance versus generated code?

This is treated as unresolved until a reply is received. In the meantime, the project has defaulted to the more conservative reading available (AI used for advice, review, and scaffolding discussion; all code written, reviewed, and understood by the author — see `AI-USAGE.md`).

---

## Decision 6 — Handling the Day 2 change (Amendment No. 2026-01)

### Context

`READ ME FIRST.md` (received Day 2) introduces Amendment No. 2026-01, effective 1 March 2026, which changes several figures already hard-coded into the manual text the pipeline reasons over:

- Earnings disregard: $120 → $175/month (§6.4.1(a)).
- Reporting window: 10 days → 14 days (§4.3.2), and the §9.1.4 cross-reference: 30 days → 14 days — **this is the same clause pair `ContradictionAgent` currently flags as a conflict.**
- Income thresholds (§6.6.1 table).
- Sanction rate: 20% → 15% (§10.5.2), plus a new exception (§10.5.3A).
- A transitional rule (§5): some changes apply to any determination made on/after 1 March 2026 regardless of the underlying period; the reporting-window change applies only where the change of circumstances itself occurred on/after 1 March 2026; claims spanning the cutover are apportioned.

This is exactly the kind of change the original problem document warned about ("keeping your retrieval, your answer construction, and your refusal logic separable enough that one of them can move without the other two being rewritten"). Because retrieval, validation, contradiction detection, and answer generation were already kept as separate modules (Decision 1), the amendment is additive rather than a rewrite — but it is **not yet done**.

### What was changed already

- The amendment file was added to the repository and read in full.
- This decision entry, documenting the plan, was written before implementation, per the Day 2 instructions.

### What was deliberately not changed yet, and the plan

- **Not changed:** `parser.py` still ingests only `data/policy-manual.md`. The pipeline has no notion of a claim date and no versioned view of a clause.
- **Plan:** extend `Clause` (in `src/models/schemas.py`) with an `effective_from` field, parse the amendment as a second small set of clause overrides keyed by the transitional rules in §5 of the amendment (some by determination date, some by the date the underlying change occurred), and have `main.py` prompt for (or accept as an argument) the relevant date before running retrieval, so the correct figure and the correct §4.3.2/§9.1.4 relationship are used per question.
- **What this would have been done differently with more warning:** the manual's own amendment mechanism was already described in §1.2.3 of the consolidated text before Day 2 even arrived ("the amended text applies to determinations made on or after the effective date of the amendment, except where the amendment provides otherwise"). In hindsight, `Clause.effective_from` should have been part of the schema from the start rather than added reactively — the corpus was telling us this was coming.

This gap is disclosed in `README.md` Section 9 as well, so it is not discovered by a judge mid-demo.