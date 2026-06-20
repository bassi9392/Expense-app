"""
app.py — Streamlit Chat UI for the Persona-Adaptive Customer Support Agent.

Run with:
    streamlit run app.py
"""

import json
import logging
import sys
import os

import streamlit as st

# ── Page config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="SupportDesk AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Path fix so `src` imports resolve when running from project root ────────────
sys.path.insert(0, os.path.dirname(__file__))

from src.config import GEMINI_API_KEY
from src.rag_pipeline import LocalRAGPipeline
from src.classifier import classify_customer_persona
from src.generator import generate_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS — clean, modern dark-accent design
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Main background ── */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.05);
    border-right: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
}
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }

/* ── Header ── */
.app-header {
    text-align: center;
    padding: 2rem 1rem 1rem;
}
.app-header h1 {
    font-size: 2.4rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.5px;
    margin: 0;
}
.app-header p {
    color: rgba(255,255,255,0.6);
    font-size: 1rem;
    margin-top: 0.3rem;
}

/* ── Chat container ── */
.chat-container {
    max-width: 820px;
    margin: 0 auto;
    padding: 1rem;
}

/* ── Message bubbles ── */
.msg-user {
    display: flex;
    justify-content: flex-end;
    margin: 0.6rem 0;
}
.msg-user .bubble {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 4px 18px;
    max-width: 72%;
    font-size: 0.95rem;
    line-height: 1.55;
    box-shadow: 0 4px 15px rgba(102,126,234,0.35);
}

.msg-agent {
    display: flex;
    justify-content: flex-start;
    margin: 0.6rem 0;
}
.msg-agent .bubble {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    color: #e8e8e8;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 18px 4px;
    max-width: 72%;
    font-size: 0.95rem;
    line-height: 1.55;
    backdrop-filter: blur(8px);
}

.msg-escalated .bubble {
    background: rgba(255, 80, 80, 0.12);
    border: 1px solid rgba(255,100,100,0.3);
    color: #ffcccc;
}

/* ── Persona badge ── */
.persona-badge {
    display: inline-block;
    padding: 0.18rem 0.65rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.badge-tech    { background: rgba(56,189,248,0.2);  color: #38bdf8; border: 1px solid #38bdf8; }
.badge-frust   { background: rgba(251,146,60,0.2);  color: #fb923c; border: 1px solid #fb923c; }
.badge-exec    { background: rgba(167,139,250,0.2); color: #a78bfa; border: 1px solid #a78bfa; }
.badge-escalated { background: rgba(248,113,113,0.2); color: #f87171; border: 1px solid #f87171; }

/* ── Score meter ── */
.score-bar-wrap {
    margin-top: 0.4rem;
    font-size: 0.75rem;
    color: rgba(255,255,255,0.45);
}
.score-bar {
    height: 4px;
    border-radius: 2px;
    background: rgba(255,255,255,0.1);
    margin-top: 3px;
    overflow: hidden;
}
.score-fill {
    height: 100%;
    border-radius: 2px;
    background: linear-gradient(90deg, #667eea, #a78bfa);
}

/* ── Input area ── */
.stTextInput input {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important;
    color: white !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.95rem !important;
}
.stTextInput input:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102,126,234,0.25) !important;
}
.stTextInput input::placeholder { color: rgba(255,255,255,0.35) !important; }

/* ── Buttons ── */
.stButton button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.4rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: opacity 0.2s !important;
}
.stButton button:hover { opacity: 0.88 !important; }

/* ── Handoff JSON ── */
.handoff-box {
    background: rgba(0,0,0,0.35);
    border: 1px solid rgba(248,113,113,0.35);
    border-radius: 10px;
    padding: 1rem;
    font-family: 'Courier New', monospace;
    font-size: 0.78rem;
    color: #ffcccc;
    margin-top: 0.5rem;
    max-height: 260px;
    overflow-y: auto;
    white-space: pre-wrap;
}

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.08) !important; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 0.75rem;
}
[data-testid="metric-container"] label { color: rgba(255,255,255,0.5) !important; font-size: 0.75rem !important; }
[data-testid="metric-container"] [data-testid="metric-value"] { color: white !important; font-size: 1.4rem !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #667eea !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INITIALISATION
# ─────────────────────────────────────────────────────────────────────────────
def _init_state() -> None:
    defaults = {
        "messages":          [],   # list of {role, content, persona, score, escalated, handoff}
        "rag_ready":         False,
        "pipeline":          None,
        "turn_count":        0,
        "frustration_turns": 0,
        "total_escalations": 0,
        "personas_seen":     [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ─────────────────────────────────────────────────────────────────────────────
# CACHED RAG PIPELINE
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_pipeline() -> LocalRAGPipeline:
    pipeline = LocalRAGPipeline()
    if pipeline.is_index_empty():
        pipeline.build_index()
    return pipeline


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
PERSONA_BADGE_CLASS = {
    "Technical Expert":   "badge-tech",
    "Frustrated User":    "badge-frust",
    "Business Executive": "badge-exec",
}
PERSONA_EMOJI = {
    "Technical Expert":   "⚙️",
    "Frustrated User":    "😤",
    "Business Executive": "💼",
}


def _badge_html(persona: str, escalated: bool = False) -> str:
    if escalated:
        return '<span class="persona-badge badge-escalated">🚨 Escalated</span>'
    cls   = PERSONA_BADGE_CLASS.get(persona, "badge-tech")
    emoji = PERSONA_EMOJI.get(persona, "")
    return f'<span class="persona-badge {cls}">{emoji} {persona}</span>'


def _score_bar(score: float) -> str:
    pct   = int(score * 100)
    color = "#22c55e" if score >= 0.6 else "#f59e0b" if score >= 0.45 else "#ef4444"
    return (
        f'<div class="score-bar-wrap">Confidence: {pct}%'
        f'<div class="score-bar"><div class="score-fill" style="width:{pct}%;background:{color}"></div></div>'
        f"</div>"
    )


def _render_messages() -> None:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="msg-user"><div class="bubble">{msg["content"]}</div></div>',
                unsafe_allow_html=True,
            )
        else:
            escalated = msg.get("escalated", False)
            extra_cls = " msg-escalated" if escalated else ""
            badge     = _badge_html(msg.get("persona", ""), escalated)
            score_bar = _score_bar(msg.get("score", 0.0))
            content   = msg["content"].replace("\n", "<br>")

            st.markdown(
                f'<div class="msg-agent{extra_cls}">'
                f'<div class="bubble">'
                f'{badge}<br>'
                f'{content}'
                f'<br>{score_bar}'
                f"</div></div>",
                unsafe_allow_html=True,
            )

            if escalated and msg.get("handoff"):
                with st.expander("📋 Human Agent Handoff Report", expanded=False):
                    st.markdown(
                        f'<div class="handoff-box">{msg["handoff"]}</div>',
                        unsafe_allow_html=True,
                    )


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## 🎯 SupportDesk AI")
        st.markdown("*Persona-Adaptive Support Agent*")
        st.divider()

        # Live stats
        st.markdown("### 📊 Session Stats")
        col1, col2 = st.columns(2)
        col1.metric("Turns", st.session_state.turn_count)
        col2.metric("Escalations", st.session_state.total_escalations)

        if st.session_state.personas_seen:
            from collections import Counter
            counts = Counter(st.session_state.personas_seen)
            st.markdown("**Persona Breakdown**")
            for p, c in counts.items():
                emoji = PERSONA_EMOJI.get(p, "")
                st.markdown(f"{emoji} **{p}**: {c}")

        st.divider()

        # Knowledge base status
        st.markdown("### 📚 Knowledge Base")
        if st.session_state.rag_ready:
            st.success("✅ Index loaded & ready")
        else:
            st.warning("⏳ Initialising…")

        st.divider()

        # Confidence threshold info
        st.markdown("### ⚙️ Escalation Rules")
        st.markdown("""
- 🔴 Confidence < **0.45** → escalate
- 🔴 Billing / refund keywords → escalate  
- 🔴 3+ frustrated turns → escalate
- 🔴 No matching docs → escalate
        """)

        st.divider()

        # Test scenarios
        st.markdown("### 🧪 Test Scenarios")
        scenarios = {
            "👨‍💻 Tech — API 401 error": "Our production API key is returning a 401 Unauthorized error. I've checked the header format and the key is active. Could this be a scoping issue?",
            "😤 Frustrated — Nothing loads": "I've been trying to access my dashboard for an hour and NOTHING is loading! This is completely unacceptable. I have a client presentation in 30 minutes!",
            "💼 Exec — SLA & uptime": "Our operational uptime is decreasing. What is the SLA guarantee and when can we expect billing disputes to be resolved?",
            "👨‍💻 Tech — Webhook not firing": "My webhook endpoint is configured but not receiving events. The URL is public HTTPS. How do I verify the signature?",
            "😤 Escalate — Duplicate charge": "I have a duplicate charge on my account from last week. I demand an immediate refund! This is fraud!",
        }
        for label, text in scenarios.items():
            if st.button(label, key=f"btn_{label}", use_container_width=True):
                st.session_state["prefill"] = text
                st.rerun()

        st.divider()
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            for key in ["messages", "turn_count", "frustration_turns",
                        "total_escalations", "personas_seen"]:
                st.session_state[key] = [] if isinstance(st.session_state[key], list) else 0
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    # ── API key guard ──────────────────────────────────────────────────────────
    if not GEMINI_API_KEY:
        st.error(
            "⚠️  **GEMINI_API_KEY not found.**  \n"
            "Create a `.env` file in the project root with:\n\n"
            "```\nGEMINI_API_KEY=your_actual_key_here\n```"
        )
        st.stop()

    # ── Sidebar ────────────────────────────────────────────────────────────────
    _render_sidebar()

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="app-header">
        <h1>🎯 SupportDesk AI</h1>
        <p>Intelligent support that adapts to <em>you</em> — technical, empathetic, or executive-ready.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Load RAG pipeline ──────────────────────────────────────────────────────
    if not st.session_state.rag_ready:
        with st.spinner("🔄 Loading knowledge base and building vector index…"):
            try:
                st.session_state.pipeline = load_pipeline()
                st.session_state.rag_ready = True
            except Exception as e:
                st.error(f"❌ Failed to initialise knowledge base: {e}")
                st.stop()

    pipeline: LocalRAGPipeline = st.session_state.pipeline

    # ── Render chat history ────────────────────────────────────────────────────
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center; padding: 3rem 1rem; color: rgba(255,255,255,0.4);">
            <div style="font-size:3rem">💬</div>
            <p style="font-size:1rem; margin-top:0.5rem">
                Start typing your question below, or pick a test scenario from the sidebar.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        _render_messages()

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Input area ─────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)

    # Handle sidebar scenario prefill
    prefill_value = st.session_state.pop("prefill", "")

    with st.form("chat_form", clear_on_submit=True):
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            user_input = st.text_input(
                label="Message",
                value=prefill_value,
                placeholder="Describe your issue… (e.g. 'I keep getting 401 errors from your API')",
                label_visibility="collapsed",
            )
        with col_btn:
            submitted = st.form_submit_button("Send ➤", use_container_width=True)

    # ── Process submission ─────────────────────────────────────────────────────
    if submitted and user_input.strip():
        query = user_input.strip()

        # Append user message
        st.session_state.messages.append({"role": "user", "content": query})
        st.session_state.turn_count += 1

        with st.spinner("🤔 Analysing your message…"):
            # Step 1 — Classify persona
            classification = classify_customer_persona(query)
            persona     = classification["persona"]
            clf_score   = classification["confidence"]

            # Track frustration streaks
            if persona == "Frustrated User":
                st.session_state.frustration_turns += 1
            else:
                st.session_state.frustration_turns = 0

            st.session_state.personas_seen.append(persona)

            # Step 2 — Retrieve context
            context_chunks = pipeline.retrieve(query)

            # Step 3 — Generate adaptive response
            result = generate_response(
                user_query=query,
                persona=persona,
                context_chunks=context_chunks,
                frustration_turns=st.session_state.frustration_turns,
                turn_count=st.session_state.turn_count,
            )

        # Track escalations
        if result["escalated"]:
            st.session_state.total_escalations += 1

        # Append agent message
        st.session_state.messages.append({
            "role":      "agent",
            "content":   result["response"],
            "persona":   persona,
            "score":     result.get("best_score", 0.0),
            "escalated": result["escalated"],
            "handoff":   result.get("handoff_summary"),
        })

        st.rerun()


if __name__ == "__main__":
    main()
