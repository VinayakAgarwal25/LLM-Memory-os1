# ===============================
# Memory OS Configuration
# ===============================


# ===============================
# OLLAMA CONFIG
# ===============================

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"
OLLAMA_EMBED_MODEL = "nomic-embed-text"



# ===============================
# STORAGE CONFIG
# ===============================

import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "Main Application", "data")

MEMORY_STORE_FILE = os.path.join(DATA_DIR, "memories.json")
VECTOR_STORE_FILE = os.path.join(DATA_DIR, "vectors.faiss")
ANALYTICS_LOG_FILE = os.path.join(DATA_DIR, "analytics.log")



# ===============================
# MEMORY SCORING CONFIG
# ===============================

LONG_TERM_THRESHOLD = 0.8
SHORT_TERM_THRESHOLD = 0.5
DISCARD_THRESHOLD = 0.3

SHORT_TERM_EXPIRY_DAYS = 30
MEDIUM_TERM_EXPIRY_DAYS = 7


# ===============================
# MEMORY RETRIEVAL CONFIG
# ===============================

MAX_MEMORIES_TO_RETRIEVE = 5
MIN_IMPORTANCE_THRESHOLD = 0.3
MIN_STORAGE_CONFIDENCE = 0.35
MIN_EXTRACTION_CONFIDENCE = 0.25

RETRIEVAL_STRATEGY = "hybrid"

SEMANTIC_WEIGHT = 0.6
IMPORTANCE_WEIGHT = 0.3
FRESHNESS_WEIGHT = 0.1
DECAY_BIAS_WEIGHT = 0.1
SHORT_TERM_TIER_BONUS = 0.05
LONG_TERM_TIER_BONUS = 0.08
MIN_SEMANTIC_RELEVANCE = 0.48
MAX_CONTEXT_MEMORIES = 3

RECENCY_WINDOW_TURNS = 1500
VECTOR_CANDIDATE_K = 128
CANDIDATE_HARD_CAP = 200
SHORT_TERM_RETRIEVAL_QUOTA = 0.4
LONG_TERM_RETRIEVAL_QUOTA = 0.6

RETRIEVAL_CACHE_SIZE = 200
RETRIEVAL_CACHE_TTL_TURNS = 5
ENABLE_RETRIEVAL_CACHE = False
TRACE_TOP_N = 5


# ===============================
# AGING CONFIG
# ===============================

AGING_ENABLED = True
RUN_AGING_EVERY_N_TURNS = 3
DECAY_RATE = 0.05
LONG_TERM_ARCHIVE_DAYS = 90
LONG_TERM_MIN_IMPORTANCE_TO_KEEP = 0.35



# ===============================
# COMPRESSION CONFIG
# ===============================

COMPRESSION_ENABLED = False
SIMILARITY_THRESHOLD = 0.85
MIN_MEMORIES_FOR_COMPRESSION = 3
CONFLICT_SIMILARITY_THRESHOLD = 0.92


# ===============================
# PROMPT CONFIG
# ===============================

SYSTEM_PROMPT = """You are a helpful AI assistant with long-term memory.
Use provided user context when relevant, but respond naturally."""


# ===============================
# DEBUG CONFIG
# ===============================

DEBUG = False
VERBOSE = False
SAVE_EVERY_TURN = True
ENABLE_ANALYTICS = True
REINFORCEMENT_ENABLED = True
REINFORCEMENT_MIN_CONFIDENCE = 0.70
REINFORCEMENT_LONG_TERM_ONLY = True
REINFORCEMENT_DELTA = 0.01
EVAL_OUTPUT_MODE = False


# ===============================
# VALIDATION
# ===============================

def validate_config():
    if not OLLAMA_BASE_URL:
        raise ValueError("OLLAMA_BASE_URL missing")

    if not OLLAMA_MODEL:
        raise ValueError("OLLAMA_MODEL missing")

    if not OLLAMA_EMBED_MODEL:
        raise ValueError("OLLAMA_EMBED_MODEL missing")

    print("Ollama configuration validated")


validate_config()
