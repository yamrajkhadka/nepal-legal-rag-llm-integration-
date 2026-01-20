import os

EMBEDDING_MODEL = "all-mpnet-base-v2"
LLM_MODEL = "llama-3.1-8b-instant"

TOP_K = 6
TEMPERATURE = 0.0
MAX_TOKENS = 350

EMBEDDINGS_PATH = "final_legal_embeddings.npy"
METADATA_PATH = "final_legal_laws_metadata.json"

GROQ_API_KEY = os.getenv(
    "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"
)
