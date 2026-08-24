class EvidenceAgent:
    def run(self, clauses, date_info):
        version = date_info.get("version")

        if not version:
            return clauses
        evidence = []

        for clause in clauses:
            if version == "original":
                evidence.append(clause)
            elif version == "amended":
                evidence.append(clause)

        return evidence