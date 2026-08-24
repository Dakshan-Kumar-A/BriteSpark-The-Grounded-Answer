def make_citation(clause):
    return (
        f"{clause.source} | "
        f"§{clause.section} | "
        f"lines {clause.start_line}-"
        f"{clause.end_line}"
    )

def validate_citations(citations):
    return all(
        citation
        for citation in citations
    )