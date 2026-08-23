class SessionMemory:
    def __init__(self):
        self.pending_query = None

    def save(self, query):
        self.pending_query = query

    def combine(self, reply):
        if not self.pending_query:
            return reply

        query = (
            self.pending_query
            + "\n"
            + reply
        )

        self.pending_query = None

        return query

    def clear(self):
        self.pending_query = None