from dataclasses import dataclass
from enum import Enum
from typing import Optional

@dataclass
class Clause:
    section: str
    text: str
    source: str
    start_line: int
    end_line: int
    @property
    def citation(self) -> str:
        return self.section

@dataclass
class RetrievedClause:
    clause: Clause
    score: float
    source: str
    @property
    def section(self) -> str:
        return self.clause.section
    @property
    def text(self) -> str:
        return self.clause.text
    @property
    def citation(self) -> str:
        return self.clause.citation
    @property
    def start_line(self) -> int:
        return self.clause.start_line
    @property
    def end_line(self) -> int:
        return self.clause.end_line
    @property
    def document_source(self) -> str:
        return self.clause.source

class Status(Enum):
    ANSWERED = "answered"
    DATE_REQUIRED = "date_required"
    CONFLICT = "conflict"
    REFUSED = "refused"

@dataclass
class AnswerResult:
    status: Status
    answer: str
    reason: Optional[str] = None
    citations: Optional[list] = None
    follow_up: Optional[str] = None
    policy_date: Optional[str] = None