# vectorstore/vector_store.py
import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)


class LegalVectorStore:
    def __init__(
        self,
        embedding_path: str,
        metadata_path: str,
        model_name="all-mpnet-base-v2"
    ):
        logger.info("[VECTOR] Initializing vector store")
        logger.info(f"[VECTOR] Embeddings file: {embedding_path}")
        logger.info(f"[VECTOR] Metadata file: {metadata_path}")
        logger.info(f"[VECTOR] Embedding model: {model_name}")

        # Load sentence transformer
        logger.info("[VECTOR] Loading sentence transformer model")
        self.embedder = SentenceTransformer(model_name)
        logger.info("[VECTOR] Sentence transformer loaded")

        # Load embeddings
        logger.info("[VECTOR] Loading embeddings into memory")
        self.embeddings = np.load(embedding_path)
        logger.info("[VECTOR] Embeddings loaded successfully")
        logger.info(f"[VECTOR] Embedding matrix shape: {self.embeddings.shape}")
        logger.info(f"[VECTOR] Total documents: {self.embeddings.shape[0]}")
        logger.info(f"[VECTOR] Embedding dimension: {self.embeddings.shape[1]}")

        # Load metadata
        logger.info("[VECTOR] Loading metadata")
        with open(metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
        logger.info("[VECTOR] Metadata loaded")
        logger.info(f"[VECTOR] Metadata entries: {len(self.metadata)}")

        # Build FAISS index
        logger.info("[VECTOR] Building FAISS index")
        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(self.embeddings)
        logger.info("[VECTOR] FAISS index ready")
        logger.info(f"[VECTOR] Indexed vectors: {self.index.ntotal}")

        logger.info("[VECTOR] Vector store initialization complete")

    def search(self, query: str, k: int = 1):
        logger.info("=" * 80)
        logger.info("[SEARCH] Vector search started")
        logger.info("=" * 80)

        logger.info(f"[SEARCH] Query text: {query}")
        logger.info(f"[SEARCH] Requested top-k results: {k}")

        # Encode query
        logger.info("[SEARCH] Encoding query")
        q_emb = self.embedder.encode([query], convert_to_numpy=True)
        logger.info("[SEARCH] Query encoded")
        logger.info(f"[SEARCH] Query embedding shape: {q_emb.shape}")

        # Perform FAISS search
        logger.info("[SEARCH] Searching FAISS index")
        distances, indices = self.index.search(q_emb, k)
        logger.info("[SEARCH] FAISS search completed")
        logger.info(f"[SEARCH] Raw results returned: {len(indices[0])}")

        # Log distance values
        logger.info("[SEARCH] Distance scores (lower is more similar):")
        for i, (idx, dist) in enumerate(zip(indices[0], distances[0])):
            logger.info(f"Result {i + 1}: Index {idx}, Distance {dist:.4f}")

        # Deduplicate results
        logger.info("[SEARCH] Deduplicating results")
        results = []
        seen = set()

        for i, idx in enumerate(indices[0]):
            item = self.metadata[idx]
            key = f"{item.get('section')}-{item.get('subsection')}"

            if key not in seen:
                seen.add(key)
                results.append(item)
                logger.info(
                    f"Result {i + 1}: "
                    f"Chapter {item.get('chapter')} "
                    f"Section {item.get('section')} (added)"
                )
            else:
                logger.info(
                    f"Result {i + 1}: "
                    f"Chapter {item.get('chapter')} "
                    f"Section {item.get('section')} (duplicate skipped)"
                )

        logger.info("[SEARCH] Deduplication complete")
        logger.info(f"[SEARCH] Unique results count: {len(results)}")

        # Final result summary
        logger.info("[SEARCH] Final result summary:")
        for i, item in enumerate(results):
            logger.info(
                f"{i + 1}. Chapter {item.get('chapter')} "
                f"Section {item.get('section')} | "
                f"Text length: {len(item.get('text', ''))} characters"
            )

        logger.info("=" * 80)
        logger.info("[SEARCH] Vector search finished")
        logger.info("=" * 80)

        return results
