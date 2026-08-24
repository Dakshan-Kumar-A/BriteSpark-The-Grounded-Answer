# AI Usage Disclosure

**Project:** The Grounded Answer (Brite Spark 2026, Problem 1)
**Author responsible for all submitted work:** Dakshan Kumar A

This document discloses how AI tools were used during development, consistent with the working agreement followed throughout: **AI tools were used for advice, review, discussion, and early-stage scaffolding assistance. All final code, architecture decisions, testing, and submitted deliverables were reviewed, understood, and approved by the author.**

The author remains responsible for every part of the submitted repository and can explain and justify the implementation and design decisions.

---

## Tools used

### Claude (Anthropic) — primary advisory and review role

Claude was used throughout development as a design and decision-review partner. Its role was to discuss possible approaches, trade-offs, risks, and edge cases. The author made the final decisions and reviewed the resulting implementation.

Specific areas where Claude's input was requested include:

* **Technology stack selection.** Discussed retrieval and LLM options for a small, static policy corpus under hackathon time constraints. This included comparing lightweight retrieval approaches with heavier frameworks and discussing a hybrid retrieval approach using `rank-bm25` and `sentence-transformers`.

* **Architecture design.** Discussed separating the system into retrieval, evidence validation, contradiction detection, answer generation, and validation stages. This separation was intended to make the system easier to understand, test, and modify when the Day 2 requirement change was introduced.

* **Dependency risk.** Discussed the installation and runtime implications of using `sentence-transformers`, including its dependency on heavier machine-learning packages and the first-run download of the embedding model. These risks were considered when documenting project setup.

* **Refusal calibration.** Discussed the trade-off involved in setting a retrieval-confidence threshold for refusing to answer. The final threshold and refusal behaviour were chosen and implemented by the author. The reasoning behind the chosen boundary is documented in `DECISIONS.md`.

* **Contradiction handling.** Discussed approaches for identifying situations where relevant clauses appear to give incompatible answers, rather than silently selecting one clause.

* **Day 2 amendment handling.** Discussed the impact of the Day 2 requirement change, which introduced Amendment No. 2026-01 and required answers to depend on the relevant date. The amendment became part of the policy corpus, and its transitional provisions distinguish between changes occurring before and after 1 March 2026.

* **Documentation review.** Assisted in reviewing the structure and clarity of `README.md`, `DECISIONS.md`, and this disclosure so that the documentation reflects the repository's actual design, tests, limitations, and Day 2 changes.

---

### ChatGPT — discussion and early development assistance

ChatGPT was used during development for:

* Discussing possible Python project folder structures.
* Confirming and discussing suitable library dependencies for `requirements.txt`.
* Discussing how a grounded RAG pipeline could be separated into retrieval, evidence validation, contradiction detection, and answer generation.
* Providing early boilerplate and scaffolding suggestions that were subsequently reviewed and adapted by the author.
* Helping generate ideas for evaluation questions, edge cases, date-based questions, refusal cases, and contradiction tests.
* Discussing debugging results and possible causes when evaluation cases did not behave as expected.
* Reviewing whether test queries were suitable for probing the project's grounded-answer, refusal, contradiction, and temporal reasoning behaviour.

ChatGPT was used as an assistance and discussion tool. The author reviewed all suggestions and retained responsibility for deciding what to implement.

---

## How AI assistance was used

AI tools were used to support the development process by helping with:

* Exploring alternative technical approaches.
* Identifying possible edge cases and failure modes.
* Discussing retrieval and refusal trade-offs.
* Reviewing architecture choices.
* Generating ideas for testing and evaluation.
* Assisting with debugging and interpretation of program output.
* Reviewing and improving the clarity and structure of documentation.

Suggestions from AI tools were not accepted automatically. The author evaluated, modified, rejected, or implemented suggestions based on the requirements of the problem and the actual behaviour of the project.

---

## What AI assistance was not used for

* **AI tools were not treated as a source of policy content.** The policy manual and Amendment No. 2026-01 are the authorities used by the application when answering policy questions. The original problem explicitly states that the manual is the authority, and the Day 2 amendment subsequently became part of the corpus.

* The system is intended to answer from the supplied policy materials rather than general knowledge or assumptions.

* AI tools did not make autonomous decisions about which implementation choices would be included in the final project.

* No AI tool had authority to independently commit or submit work on the author's behalf.

* AI-generated suggestions were reviewed before use rather than being treated as automatically correct.

* Expected results for the evaluation cases were reviewed against the supplied policy materials and the intended system behaviour.

---

## Day 2 requirement change

On Day 2, Amendment No. 2026-01 was introduced and took effect on **1 March 2026**. The project requirements changed so that answers must be correct for the relevant date of the claim, determination, or change of circumstances being asked about. The consolidated manual remained in place, with the amendment modifying specific provisions and adding transitional rules.

This requirement introduced an additional temporal reasoning requirement. For example, the amendment changes reporting deadlines and specifies that, for changes of circumstances, the applicable reporting period depends on the date on which the change occurred. A change occurring before 1 March 2026 continues to use the period applicable at that date, regardless of when the determination is made.
The project design was reviewed and updated around this requirement while keeping retrieval, evidence checking, contradiction handling, and answer construction as separate concerns.

---

## Accountability statement

The author, **Dakshan Kumar A**, takes responsibility for the submitted project, including its code, architectural decisions, evaluation cases, documentation, and known limitations.

The author can explain:

* The retrieval approach and why it was selected.
* How BM25 and semantic retrieval are combined.
* How evidence is selected and validated.
* How the system distinguishes between answering, refusing, and identifying a conflict.
* The reasoning behind the retrieval-confidence threshold.
* How clause-level citations are produced.
* How contradictory policy provisions are handled.
* How the Day 2 amendment and its effective and transitional dates affect answers.
* The evaluation methodology and the purpose of the test cases.
* The current limitations and trade-offs of the implementation.

AI tools were used as development aids for discussion, review, exploration, and early-stage assistance. **The author remains fully responsible for the final submitted work and its correctness.**
