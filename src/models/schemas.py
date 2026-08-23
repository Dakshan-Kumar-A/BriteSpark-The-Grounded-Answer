from dataclasses import dataclass
from enum import Enum


class Status(Enum):
    ANSWERED = "ANSWERED"
    DATE_REQUIRED = "DATE_REQUIRED"
    CONFLICT = "CONFLICT"
    REFUSED = "REFUSED"


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


@dataclass
class AnswerResult:
    status: Status
    answer: str
    reason: str = ""
    citations: list = None
    policy_date: str = None
    follow_up: str = None

    def __post_init__(self):
        if self.citations is None:
            self.citations = []