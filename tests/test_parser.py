from src.config import DATA_PATH

from src.ingestion.parser import parse_policy


def test_policy_is_parsed():
    clauses = parse_policy(DATA_PATH)

    assert len(clauses) > 0


def test_clause_has_citation():
    clauses = parse_policy(DATA_PATH)

    first_clause = clauses[0]

    assert first_clause.citation


def test_known_clause_exists():
    clauses = parse_policy(DATA_PATH)

    citations = [
        clause.citation
        for clause in clauses
    ]

    assert "4.3.2" in citations