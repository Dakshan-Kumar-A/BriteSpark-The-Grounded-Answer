import re

from src.models.schemas import Clause


CLAUSE_PATTERN = r"^\*\*(\d+\.\d+\.\d+)\*\*\s*(.*)"


def parse_policy(file_path):
    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        lines = file.readlines()

    clauses = []
    current = None
    current_part = ""
    current_title = ""

    for line in lines:
        line = line.strip()

        if line.startswith("# Part"):
            current_part = line.replace("# ", "")
            continue

        if line.startswith("## "):
            current_title = line.replace("## ", "")
            continue

        match = re.match(
            CLAUSE_PATTERN,
            line
        )

        if match:
            if current:
                clauses.append(current)

            citation = match.group(1)
            text = match.group(2)

            current = Clause(
                citation=citation,
                text=text,
                title=current_title,
                part=current_part
            )

        elif current and line:
            current.text += " " + line

    if current:
        clauses.append(current)

    return clauses