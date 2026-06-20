"""
classifier.py — Detects the customer's communication persona from their message.

Returns a structured dict:
    {
        "persona":    "Technical Expert" | "Frustrated User" | "Business Executive",
        "confidence": 0.0 – 1.0,
        "reasoning":  "<short explanation>"
    }
"""

import json
import time
import random
import logging

from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, GEMINI_CHAT_MODEL, PERSONAS

logger = logging.getLogger(__name__)


# ── System prompt ──────────────────────────────────────────────────────────────
_SYSTEM_INSTRUCTION = (
    "You are an advanced NLP classification engine embedded in a customer-support platform. "
    "Your ONLY job is to read the customer's message and classify it into exactly ONE persona.\n\n"
    "Persona definitions:\n"
    "1. 'Technical Expert'     – Uses technical jargon, asks about APIs, configs, error codes, "
    "   logs, integrations, SDKs, or code.\n"
    "2. 'Frustrated User'      – Uses emotional language, exclamation marks, words like "
    "   'urgent', 'broken', 'nothing works', 'I've been waiting', or expresses clear anger/anxiety.\n"
    "3. 'Business Executive'   – Focuses on business impact, ROI, SLAs, timelines, operational "
    "   continuity, and prefers brevity over technical depth.\n\n"
    "Return ONLY a valid JSON object — no prose, no markdown fences — matching this schema:\n"
    '{ "persona": "<one of the three labels>", "confidence": <float 0-1>, "reasoning": "<one sentence>" }'
)


def classify_customer_persona(user_message: str, max_retries: int = 4) -> dict:
    """
    Calls Gemini to classify the user's persona.

    Args:
        user_message: The raw text typed by the customer.
        max_retries:  How many times to retry on transient failures.

    Returns:
        A dict with keys 'persona', 'confidence', 'reasoning'.
        Falls back to 'Frustrated User' with confidence 0.0 if all retries fail.
    """
    if not GEMINI_API_KEY:
        raise EnvironmentError("GEMINI_API_KEY is not set in your .env file.")

    client = genai.Client(api_key=GEMINI_API_KEY)

    response_schema = {
        "type": "OBJECT",
        "properties": {
            "persona":    {"type": "STRING", "enum": PERSONAS},
            "confidence": {"type": "NUMBER"},
            "reasoning":  {"type": "STRING"},
        },
        "required": ["persona", "confidence", "reasoning"],
    }

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_CHAT_MODEL,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=_SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=0.1,
                ),
            )
            result = json.loads(response.text)
            # Validate persona value
            if result.get("persona") not in PERSONAS:
                result["persona"] = "Frustrated User"
            result["confidence"] = float(result.get("confidence", 0.5))
            logger.info("Classified persona: %s (%.2f)", result["persona"], result["confidence"])
            return result

        except Exception as exc:  # noqa: BLE001
            if attempt == max_retries - 1:
                logger.error("Persona classification failed after %d retries: %s", max_retries, exc)
                return {
                    "persona": "Frustrated User",
                    "confidence": 0.0,
                    "reasoning": "Classification failed; defaulting to Frustrated User for safety.",
                }
            sleep_s = (2 ** attempt) + random.uniform(0, 1)
            logger.warning("Attempt %d failed (%s). Retrying in %.1fs…", attempt + 1, exc, sleep_s)
            time.sleep(sleep_s)

    # Should never reach here, but satisfies type checkers
    return {"persona": "Frustrated User", "confidence": 0.0, "reasoning": "Fallback"}


# ── Quick manual test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    samples = [
        "Our production API key stopped working with a 401 Unauthorized block. Check our logs.",
        "I've been waiting for THREE HOURS and nothing is fixed! This is unacceptable!!!",
        "What is the estimated SLA for resolving our billing dispute? We need a timeline.",
    ]
    for msg in samples:
        print(f"\nMessage : {msg}")
        print(f"Result  : {json.dumps(classify_customer_persona(msg), indent=2)}")
