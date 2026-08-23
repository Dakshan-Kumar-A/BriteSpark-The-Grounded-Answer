import os

from dotenv import load_dotenv


load_dotenv()


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "policy-manual.md"
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

TOP_K = 5

MIN_RETRIEVAL_SCORE = 0.40