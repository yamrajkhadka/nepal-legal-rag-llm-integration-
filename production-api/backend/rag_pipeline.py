from vectorstore.vector_store import LegalVectorStore
from backend.llm import LegalLLM
from backend.prompts import LEGAL_PROMPT
import logging

logger = logging.getLogger(__name__)

logger.info("[MODULE] Loading RAG pipeline")

# Initialize vector store
vector_db = LegalVectorStore(
    "vectorstore/final_legal_embeddings.npy",
    "vectorstore/final_legal_laws_metadata.json"
)
logger.info("[MODULE] Vector store loaded")

# Initialize language model
llm = LegalLLM()
logger.info("[MODULE] LLM instance ready")


def answer_question(question: str):
    logger.info("=" * 80)
    logger.info("[RAG] Pipeline started")
    logger.info("=" * 80)

    logger.info(f"[RAG] Incoming question: {question}")

    # Step 1: Retrieve relevant documents
    logger.info("[RAG] Step 1: Searching vector store")
    retrieved = vector_db.search(question, k=1)  # Reduced for faster inference
    logger.info(f"[RAG] Step 1 complete: {len(retrieved)} document(s) retrieved")

    # Log metadata of retrieved documents
    logger.info("[RAG] Retrieved document metadata:")
    for idx, doc in enumerate(retrieved):
        logger.info(
            f"Document {idx + 1}: Chapter {doc.get('chapter')}, "
            f"Section {doc.get('section')}"
        )

    # Step 2: Build context from retrieved documents
    logger.info("[RAG] Step 2: Building context")
    context = "\n\n".join(
        f"[Chapter {item['chapter']} Section {item['section']}] {item['text']}"
        for item in retrieved
    )

    MAX_CONTEXT_CHARS = 1000
    context = context[:MAX_CONTEXT_CHARS]

    logger.info(f"[RAG] Step 2 complete: Context size {len(context)} characters")

    # Step 3: Create prompt
    logger.info("[RAG] Step 3: Formatting prompt")
    prompt = LEGAL_PROMPT.format(context=context, question=question)
    logger.info(f"[RAG] Step 3 complete: Prompt length {len(prompt)} characters")

    # Step 4: Generate answer using LLM
    logger.info("[RAG] Step 4: Generating answer via LLM")
    logger.info("[RAG] CPU inference may take up to 1–2 minutes")

    answer = llm.generate(prompt, max_tokens=96)

    logger.info("[RAG] Step 4 complete: Answer generated")
    logger.info(f"[RAG] Answer length: {len(answer)} characters")

    logger.info("=" * 80)
    logger.info("[RAG] Pipeline finished")
    logger.info("=" * 80)

    return answer
