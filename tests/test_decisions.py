from src.validation.date_resolver import (
    DateResolver,
)

def test_old_policy():
    resolver = DateResolver()
    result = resolver.resolve(
        "What was the earnings disregard "
        "for a determination on 2026-02-20?"
    )
    assert result["version"] == "original"

def test_new_policy():
    resolver = DateResolver()
    result = resolver.resolve(
        "What was the earnings disregard "
        "for a determination on 2026-03-20?"
    )
    assert result["version"] == "amended"

def test_missing_change_date():
    resolver = DateResolver()
    result = resolver.resolve(
        "What is the reporting deadline?"
    )
    assert result["needed"] is True

def test_reporting_date():
    resolver = DateResolver()
    result = resolver.resolve(
        "What is the reporting deadline "
        "for a change on 2026-03-10?"
    )
    assert result["version"] == "amended"