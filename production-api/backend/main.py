from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.rag_pipeline import answer_question
import logging
import time

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("[STARTUP] Initializing Nepal Legal RAG API")
logger.info("=" * 80)

# FastAPI application setup
app = FastAPI(
    title="Nepal Legal RAG API",
    description="Legal assistance based on National Penal Code of Nepal, 2017",
    version="1.0.0"
)

logger.info("[STARTUP] FastAPI application created")

# Enable CORS for external frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("[STARTUP] CORS middleware enabled")

# Request / response schemas
class Query(BaseModel):
    question: str


class HealthResponse(BaseModel):
    status: str
    message: str


@app.get("/", response_model=HealthResponse)
def read_root():
    logger.info("[ENDPOINT] GET /")
    return {
        "status": "healthy",
        "message": "Nepal Legal RAG API is running"
    }


@app.get("/health", response_model=HealthResponse)
def health_check():
    logger.info("[ENDPOINT] GET /health")
    return {
        "status": "healthy",
        "message": "All systems operational"
    }


@app.post("/ask")
def ask(query: Query):
    request_id = str(int(time.time() * 1000))

    logger.info("=" * 80)
    logger.info(f"[REQUEST {request_id}] POST /ask received")
    logger.info("=" * 80)

    try:
        # Input validation
        logger.info(f"[REQUEST {request_id}] Validating request payload")

        if not query.question or not query.question.strip():
            logger.error(f"[REQUEST {request_id}] Empty question provided")
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        logger.info(f"[REQUEST {request_id}] Validation successful")
        logger.info(f"[REQUEST {request_id}] Question: {query.question}")
        logger.info(f"[REQUEST {request_id}] Question length: {len(query.question)} characters")

        # Run RAG pipeline
        logger.info(f"[REQUEST {request_id}] Executing answer_question()")
        start_time = time.time()

        answer = answer_question(query.question)

        elapsed_time = time.time() - start_time

        logger.info(f"[REQUEST {request_id}] RAG pipeline completed")
        logger.info(f"[REQUEST {request_id}] Processing time: {elapsed_time:.2f} seconds")
        logger.info(f"[REQUEST {request_id}] Answer length: {len(answer)} characters")

        # Log short answer preview
        logger.info(f"[REQUEST {request_id}] Answer preview:")
        logger.info(f"{answer[:300]}...")

        response = {
            "answer": answer,
            "status": "success"
        }

        logger.info(f"[REQUEST {request_id}] Response sent successfully")
        logger.info("=" * 80)
        logger.info(f"[REQUEST {request_id}] Request finished")
        logger.info("=" * 80)

        return response

    except HTTPException:
        logger.error(f"[REQUEST {request_id}] HTTP error occurred")
        raise

    except Exception as e:
        logger.error(f"[REQUEST {request_id}] Unexpected server error")
        logger.error(f"[REQUEST {request_id}] Error type: {type(e).__name__}")
        logger.error(f"[REQUEST {request_id}] Error message: {str(e)}", exc_info=True)

        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    logger.info("[STARTUP] Launching Uvicorn on 0.0.0.0:7860")
    uvicorn.run(app, host="0.0.0.0", port=7860)
