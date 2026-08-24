import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

POLICY_PATH = DATA_DIR / "policy-manual.md"
AMENDMENT_PATH = DATA_DIR / "Amendment No. 2026-01.md"
DATA_PATHS = [POLICY_PATH,AMENDMENT_PATH,]

MIN_EVIDENCE_SCORE = 0.15
MIN_RETRIEVAL_SCORE = 0.40
EFFECTIVE_DATE = "2026-03-01"
TOP_K = 6

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"