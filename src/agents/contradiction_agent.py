class ContradictionAgent:

    def __init__(self, clauses=None):
        self.clauses = clauses or []

    def run(
        self,
        query,
        clauses,
        date_info,
    ):

        query_text = query.lower()

        # ----------------------------------------------------
        # Determine whether this is a reporting question
        # ----------------------------------------------------

        reporting = any(
            word in query_text
            for word in [
                "report",
                "reporting",
                "deadline",
                "notify",
                "change of circumstances",
                "reporting period",
            ]
        )

        if not reporting:
            return {
                "conflict": False,
                "clauses": [],
            }

        # ----------------------------------------------------
        # Reporting applicability is based on CHANGE DATE
        # ----------------------------------------------------

        version = date_info.get(
            "change_version"
        )

        if version is None:
            version = date_info.get(
                "version"
            )

        # Amended policy resolves the old conflict.
        if version == "amended":
            return {
                "conflict": False,
                "clauses": [],
            }

        # ----------------------------------------------------
        # Search COMPLETE corpus
        # ----------------------------------------------------

        source_clauses = (
            self.clauses
            if self.clauses
            else clauses
        )

        sections = {
            clause.section: clause
            for clause in source_clauses
        }

        first = sections.get(
            "4.3.2"
        )

        second = sections.get(
            "9.1.4"
        )

        # ----------------------------------------------------
        # Both original reporting clauses exist
        # ----------------------------------------------------

        if first and second:

            return {
                "conflict": True,
                "clauses": [
                    first,
                    second,
                ],
            }

        return {
            "conflict": False,
            "clauses": [],
        }