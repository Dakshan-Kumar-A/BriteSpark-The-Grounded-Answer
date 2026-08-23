class EvidenceAgent:

    def __init__(self, checker):
        self.checker = checker

    def evaluate(self, results):
        can_answer = self.checker.can_answer(
            results
        )

        reason = self.checker.get_reason(
            results
        )

        return can_answer, reason