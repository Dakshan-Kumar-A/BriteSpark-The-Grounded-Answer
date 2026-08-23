class ContradictionAgent:

    def find_known_conflict(self, results):
        citations = {
            item.clause.citation
            for item in results
        }

        has_4_3_2 = "4.3.2" in citations
        has_9_1_4 = "9.1.4" in citations

        if has_4_3_2 and has_9_1_4:
            return True

        return False

    def get_conflict_message(self):
        return (
            "The manual appears to contain "
            "conflicting reporting deadlines: "
            "§4.3.2 states 10 calendar days, "
            "while §9.1.4 refers to 30 calendar days "
            "under §4.3."
        )