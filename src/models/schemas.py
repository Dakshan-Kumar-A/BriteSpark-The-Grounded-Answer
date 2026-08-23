from dataclasses import dataclass, field


@dataclass
class Clause:
    citation: str
    text: str
    title: str = ""
    part: str = ""


@dataclass
class RetrievedClause:
    clause: Clause
    score: float
    source: str = ""


@dataclass
class AnswerResult:
    answer: str
    citations: list[str] = field(default_factory=list)
    status: str = "answered"
    reason: str = ""