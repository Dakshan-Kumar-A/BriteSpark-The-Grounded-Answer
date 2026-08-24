from src.config import (
    POLICY_PATH,
    AMENDMENT_PATH,
)
from src.ingestion.parser import (
    parse_file,
    load_corpus,
)

def test_policy_parser_returns_clauses():
    clauses = parse_file(
        POLICY_PATH,
        "policy-manual.md",
    )
    assert clauses
    assert len(clauses) > 0

def test_amendment_parser_returns_clauses():
    clauses = parse_file(
        AMENDMENT_PATH,
        "Amendment No. 2026-01.md",
    )
    assert clauses
    assert len(clauses) > 0

def test_corpus_contains_both_documents():
    clauses = load_corpus(
        POLICY_PATH,
        AMENDMENT_PATH,
    )
    assert clauses
    assert len(clauses) > 0
    sources = {
        clause.source
        for clause in clauses
    }
    assert "policy-manual.md" in sources
    assert "Amendment No. 2026-01.md" in sources

def test_clauses_have_text():
    clauses = load_corpus(
        POLICY_PATH,
        AMENDMENT_PATH,
    )
    for clause in clauses:
        assert clause.text
        assert clause.text.strip()

def test_clauses_have_section():
    clauses = load_corpus(
        POLICY_PATH,
        AMENDMENT_PATH,
    )
    for clause in clauses:
        assert clause.section
        assert clause.section.strip()

def test_clause_line_numbers_are_valid():
    clauses = load_corpus(
        POLICY_PATH,
        AMENDMENT_PATH,
    )
    for clause in clauses:
        assert clause.start_line >= 1
        assert clause.end_line >= clause.start_line