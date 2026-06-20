"""
escalator.py — Determines whether a conversation should be escalated to a human
agent and generates a structured JSON handoff report when it should.

Public API
----------
    should_escalate(chunks, user_query) -> bool
    generate_handoff(user_query, persona, chunks, turn_count) -> str  (JSON)
"""

import json
import datetime
import logging

from src.config import CONFIDENCE_THRESHOLD, SENSITIVE_KEYWORDS

logger = logging.getLogger(__name__)


# ── Escalation decision ─────────────────────────────────────────────────────────

def should_escalate(
    context_chunks: list[dict],
    user_query: str,
    frustration_turns: int = 0,
) -> tuple[bool, str]:
    """
    Returns (escalate: bool, reason: str).

    Escalation triggers (any one is sufficient):
        1. No chunks retrieved at all.
        2. Best cosine-similarity score below CONFIDENCE_THRESHOLD.
        3. Query contains sensitive keywords (billing / legal / refund etc.).
        4. User has been frustrated for 3+ consecutive turns.
    """
    # Trigger 1 — empty retrieval
    if not context_chunks:
        return True, "No relevant documentation found for this query."

    # Trigger 2 — low retrieval confidence
    best_score = max(c["score"] for c in context_chunks)
    if best_score < CONFIDENCE_THRESHOLD:
        return (
            True,
            f"Retrieval confidence too low (best score: {best_score:.3f} < threshold {CONFIDENCE_THRESHOLD}).",
        )

    # Trigger 3 — sensitive topic
    query_lower = user_query.lower()
    for kw in SENSITIVE_KEYWORDS:
        if kw in query_lower:
            return True, f"Sensitive topic detected: '{kw}'."

    # Trigger 4 — repeated frustration
    if frustration_turns >= 3:
        return True, f"Unresolved frustration detected across {frustration_turns} consecutive turns."

    return False, ""


# ── Handoff JSON generator ──────────────────────────────────────────────────────

def generate_handoff(
    user_query: str,
    persona: str,
    context_chunks: list[dict],
    turn_count: int = 1,
    escalation_reason: str = "",
) -> str:
    """
    Compiles a structured JSON ticket for the human agent who will take over.

    Returns a pretty-printed JSON string.
    """
    best_score = max((c["score"] for c in context_chunks), default=0.0)
    sources    = list({c["source"] for c in context_chunks})

    handoff = {
        "ticket": {
            "generated_at":   datetime.datetime.utcnow().isoformat() + "Z",
            "conversation_turns": turn_count,
        },
        "customer": {
            "detected_persona": persona,
            "detected_issue":   user_query[:200] + ("…" if len(user_query) > 200 else ""),
        },
        "escalation": {
            "reason":           escalation_reason or "Unspecified",
            "confidence_score": round(best_score, 4),
            "threshold":        CONFIDENCE_THRESHOLD,
        },
        "retrieval": {
            "attempted_sources": sources,
            "top_chunks_preview": [
                {"source": c["source"], "score": c["score"], "preview": c["text"][:120] + "…"}
                for c in context_chunks[:3]
            ],
        },
        "recommended_action": _recommend_action(persona, escalation_reason),
    }

    return json.dumps(handoff, indent=2)


def _recommend_action(persona: str, reason: str) -> str:
    """Returns a human-readable action recommendation for the support agent."""
    if "billing" in reason.lower() or "sensitive" in reason.lower():
        return (
            "Route to the Billing & Accounts team. "
            "Verify the customer's account, review recent transactions, and initiate a refund/dispute process if applicable."
        )
    if persona == "Technical Expert":
        return (
            "Assign to a Tier-2 Technical Engineer. "
            "Review API logs, error codes, and configuration details before responding."
        )
    if persona == "Frustrated User":
        return (
            "Assign to a senior Customer Care Specialist with empathy training. "
            "Prioritise callback within 30 minutes. Acknowledge inconvenience immediately."
        )
    if persona == "Business Executive":
        return (
            "Escalate to the Client Success Manager. "
            "Prepare a one-page status brief covering resolution timeline and business impact mitigation."
        )
    return "Review the conversation context and assign to the most appropriate specialist team."


# ── Quick manual test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample_chunks = [
        {"text": "Reset your password via the settings page.", "source": "password_reset_guide.pdf", "score": 0.38},
    ]
    escalate, reason = should_escalate(sample_chunks, "I want a full refund immediately!")
    print(f"Escalate: {escalate}  |  Reason: {reason}")
    if escalate:
        print(generate_handoff("I want a full refund!", "Frustrated User", sample_chunks, escalation_reason=reason))
