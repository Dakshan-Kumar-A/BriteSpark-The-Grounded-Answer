import re
from src.models.schemas import Clause

SECTION_RE = re.compile(
    r"^#{1,6}\s+(?:§)?(\d+(?:\.\d+)+(?:[A-Za-z])?)"
)

AMENDMENT_RE = re.compile(
    r"^\*\*(\d+(?:\.\d+)+[A-Za-z]?)\*\*"
)


def parse_file(path, source):
    lines = path.read_text(
        encoding="utf-8"
    ).splitlines()
    clauses = []
    section = None
    start_line = 1
    buffer = []

    for number, line in enumerate(
        lines,
        start=1,
    ):

        match = SECTION_RE.match(line)
        amendment = AMENDMENT_RE.match(line)
        new_section = None

        if match:
            new_section = match.group(1)

        elif source == "Amendment No. 2026-01.md" and amendment:
            new_section = amendment.group(1)

        if new_section:
            if section and buffer:
                clauses.append(
                    Clause(
                        section=section,
                        text="\n".join(buffer).strip(),
                        source=source,
                        start_line=start_line,
                        end_line=number - 1,
                    )
                )
            section = new_section
            start_line = number
            buffer = [line]
        elif section:
            buffer.append(line)

    if section and buffer:
        clauses.append(
            Clause(
                section=section,
                text="\n".join(buffer).strip(),
                source=source,
                start_line=start_line,
                end_line=len(lines),
            )
        )
    return clauses


def load_corpus(
    policy_path,
    amendment_path,
):
    policy = parse_file(
        policy_path,
        "policy-manual.md",
    )
    amendment = parse_file(
        amendment_path,
        "Amendment No. 2026-01.md",
    )

    return policy + amendment