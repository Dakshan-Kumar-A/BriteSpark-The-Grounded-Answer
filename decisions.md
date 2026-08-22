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