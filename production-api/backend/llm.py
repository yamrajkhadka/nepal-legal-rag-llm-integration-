from ctransformers import AutoModelForCausalLM
import logging

logger = logging.getLogger(__name__)


class LegalLLM:
    def __init__(self):
        # Model configuration
        self.model_id = "yamraj047/nepal-legal-mistral-7b-GGUF"
        self.model_file = "nepal-legal-Q4_K_M.gguf"

        logger.info("[INIT] Initializing LegalLLM using CTransformers")
        logger.info(f"[INIT] Model repository: {self.model_id}")
        logger.info(f"[INIT] Model file: {self.model_file}")

        logger.info("[INIT] Loading GGUF model (this may take some time)...")

        # Load model (CPU-only inference)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            model_file=self.model_file,
            model_type="mistral",
            gpu_layers=0,          # CPU inference
            context_length=1024,
            threads=8              # Adjust based on available CPU cores
        )

        logger.info("[INIT] Model loaded successfully")
        logger.info("[INIT] Running inference via CTransformers (CPU optimized)")

    def generate(self, prompt, max_tokens=96):
        """
        Generates a response from the model using the provided prompt.
        Intended for legal question-answering based on Nepal's Penal Code.
        """

        logger.info("=" * 80)
        logger.info("[GENERATION] Starting inference")
        logger.info(f"[GENERATION] Prompt length: {len(prompt)} characters")
        logger.info(f"[GENERATION] Max tokens: {max_tokens}")
        logger.info("=" * 80)

        # Preview a small portion of the prompt for debugging
        logger.info("[GENERATION] Prompt preview:")
        logger.info(f"{prompt[:200]}...")

        # Basic instruction-style system prompt
        enhanced_prompt = f"""You are a legal information assistant for Nepal's National Penal Code, 2017.
Answer ONLY using the legal text provided. Be direct and factual.
{prompt}
Answer:"""

        logger.info("[GENERATION] Generating response (CPU inference may take 1–2 minutes)...")

        import time
        start_time = time.time()

        # Run inference
        response = self.model(
            enhanced_prompt,
            max_new_tokens=max_tokens,
            temperature=0.1,
            top_p=0.8,
            repetition_penalty=1.05,
            stop=["\n\n", "Question:", "---"]
        )

        generation_time = time.time() - start_time

        logger.info("[GENERATION] Inference completed")
        logger.info(f"[GENERATION] Time taken: {generation_time:.2f} seconds")
        logger.info(f"[GENERATION] Output length: {len(response)} characters")

        # Log a short preview of the output
        logger.info("[RESULT] Response preview:")
        logger.info(f"{response[:300]}...")

        logger.info("=" * 80)
        logger.info("[GENERATION] Done")
        logger.info("=" * 80)

        return response.strip()

