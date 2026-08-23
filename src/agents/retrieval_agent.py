class RetrievalAgent:
    def __init__(self, retriever):
        self.retriever = retriever

    def run(self, query):
        return self.retriever.search(query)