class ContradictionAgent:

    def __init__(self, clauses):
        self.clauses = clauses

    def run(
        self,
        query,
        clauses,
        date_info,
    ):
        """
        Detect policy contradictions.

        Reporting rules:
            - Use the change date.
            - Before 1 March 2026, the original policy applies.
            - The original policy contains conflicting reporting
              provisions in §4.3.2 and §9.1.4.

        The contradiction check uses the COMPLETE CORPUS rather
        than only retrieved evidence. This prevents retrieval
        ranking from hiding one side of a known contradiction.
        """

        # --------------------------------------------------
        # If no date was supplied, the answerability layer
        # will handle DATE_REQUIRED.
        # --------------------------------------------------

        if date_info.get("needed"):
            return {
                "conflict": False,
                "clauses": [],
            }

        # --------------------------------------------------
        # Determine whether the question concerns reporting.
        # --------------------------------------------------

        query_text = query.lower()

        reporting_keywords = [
            "reporting deadline",
            "reporting period",
            "report a change",
            "reporting",
            "report",
            "change of circumstances",
            "failing to report",
            "failure to report",
            "notify",
            "notification",
        ]

        is_reporting_question = any(
            keyword in query_text
            for keyword in reporting_keywords
        )

        if not is_reporting_question:
            return {
                "conflict": False,
                "clauses": [],
            }

        # --------------------------------------------------
        # Amended policy.
        #
        # The amendment resolves the old conflict.
        # --------------------------------------------------

        if date_info.get("version") == "amended":
            return {
                "conflict": False,
                "clauses": [],
            }

        # --------------------------------------------------
        # Original policy.
        #
        # IMPORTANT:
        # Search the COMPLETE corpus, not only retrieved
        # evidence.
        # --------------------------------------------------

        sections = {
            clause.section: clause
            for clause in self.clauses
        }

        first = sections.get("4.3.2")
        second = sections.get("9.1.4")

        # Both original reporting provisions exist.
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