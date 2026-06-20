# 🎯 Persona-Adaptive Customer Support Agent

> An intelligent customer support chatbot built with **Google Gemini**, **ChromaDB RAG**, and **Streamlit** that dynamically adapts its response style based on the customer's communication persona.

---

## 📌 Live Demo

> **Deployed URL:** *(Add your Streamlit Cloud / Hugging Face / Railway link here after deployment)*  
> **Screen Recording:** *(Add your Loom / YouTube / Google Drive link here)*

---

## 🧠 Project Overview

Traditional support chatbots treat every user the same. This agent is different — it first **classifies who you are**, then **changes how it speaks to you**.

| Persona | Trigger | Response Style |
|---|---|---|
| ⚙️ **Technical Expert** | API jargon, error codes, config questions | Root-cause analysis, code blocks, structured steps |
| 😤 **Frustrated User** | Emotional language, urgency, complaints | Empathy-first, simple bullet steps, reassuring tone |
| 💼 **Business Executive** | SLAs, ROI, timelines, business impact | Concise, professional, outcome-focused, ≤120 words |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Message                             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              Persona Classifier (Gemini + JSON Schema)          │
│    → "Technical Expert" | "Frustrated User" | "Business Exec"  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          ▼                                 ▼
┌──────────────────┐             ┌────────────────────────────────┐
│  RAG Pipeline    │             │   Escalation Check             │
│                  │             │                                │
│  1. Embed query  │             │  • Score < 0.45 threshold?     │
│  2. ChromaDB     │             │  • Billing / refund keywords?  │
│     cosine       │             │  • 3+ frustrated turns?        │
│     similarity   │             │  • No docs found?              │
│  3. Top-K chunks │             └───────────┬────────────────────┘
└────────┬─────────┘                         │
         │                           ┌───────┴──────────┐
         │                           │                  │
         │                      YES  ▼             NO   ▼
         │              ┌──────────────────┐  ┌──────────────────────┐
         │              │  Human Handoff   │  │  Adaptive Generator  │
         │              │  JSON Report     │  │                      │
         │              │                  │  │  Persona prompt +    │
         │              │  • Ticket data   │  │  RAG context +       │
         │              │  • Customer info │  │  Gemini LLM call     │
         │              │  • Action recs   │  └──────────┬───────────┘
         │              └──────────────────┘             │
         │                                               │
         └─────────────────────────────────────────────►│
                                                         ▼
                                            ┌─────────────────────┐
                                            │  Streamlit Chat UI  │
                                            │  • Persona badge    │
                                            │  • Confidence meter │
                                            │  • Handoff expander │
                                            └─────────────────────┘
```

---

## 📁 Project Structure

```
persona-support-agent/
│
├── data/                              ← Knowledge base documents
│   ├── api_troubleshooting.md         ← API errors, auth, webhooks, SDKs
│   ├── billing_policy.txt             ← Plans, refunds, disputes, SLAs
│   ├── general_faq.txt                ← Account, interface, integrations
│   ├── security_compliance.txt        ← SSO, RBAC, encryption, compliance
│   └── password_reset_guide.pdf       ← Step-by-step reset + recovery (PDF)
│
├── src/
│   ├── __init__.py
│   ├── config.py                      ← All tuneable constants & thresholds
│   ├── classifier.py                  ← Gemini persona classification
│   ├── rag_pipeline.py                ← Document ingestion + ChromaDB retrieval
│   ├── generator.py                   ← Persona-adaptive LLM response generation
│   └── escalator.py                   ← Escalation logic + handoff JSON builder
│
├── app.py                             ← Streamlit chat UI
├── requirements.txt
├── .env.example                       ← Template for your API key
├── .gitignore
└── README.md
```

---

## ⚙️ Technical Stack

| Component | Technology |
|---|---|
| LLM | Google Gemini 2.5 Flash |
| Embeddings | Gemini `text-embedding-004` (768-dim) |
| Vector DB | ChromaDB (persistent local, cosine distance) |
| Chunking | LangChain `RecursiveCharacterTextSplitter` |
| PDF Parsing | `pypdf` |
| Web UI | Streamlit |
| Language | Python 3.11+ |

---

## 🚀 Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/persona-support-agent.git
cd persona-support-agent
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Your API Key

```bash
cp .env.example .env
```

Open `.env` and add your key:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

> Get a free Gemini API key at: https://aistudio.google.com/app/apikey

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**. On first run, it automatically indexes all documents in `./data` into ChromaDB.

---

## 🧪 Test Scenarios

Use the **sidebar buttons** or type these messages directly:

| # | Message | Expected Persona | Expected Behaviour |
|---|---|---|---|
| 1 | *"The dashboard has been loading for an hour and NOTHING works! I have a deadline!"* | 😤 Frustrated User | Empathy-first response, simple numbered steps |
| 2 | *"What are the OAuth 2.0 scopes required for the write:tickets endpoint?"* | ⚙️ Technical Expert | Structured technical answer with code/config |
| 3 | *"Our SLA shows decreasing uptime. What's the resolution timeline for billing disputes?"* | 💼 Business Executive | Short, professional, timeline-focused |
| 4 | *"My webhook isn't firing. The URL is public HTTPS. How do I verify signatures?"* | ⚙️ Technical Expert | HMAC-SHA256 snippet, webhook checklist |
| 5 | *"I have a duplicate charge from last week. I demand an immediate refund!"* | 😤 Frustrated User | **Triggers escalation** → Handoff JSON generated |

---

## 🔧 Key Concepts Explained

### RAG Pipeline (Retrieval-Augmented Generation)
Instead of relying on the LLM's training memory (which can hallucinate), the agent:
1. Converts your question into a 768-dimensional vector using Gemini embeddings
2. Searches ChromaDB for the most semantically similar document chunks
3. Injects those chunks into the LLM's prompt as grounded facts

### Cosine Similarity
Documents and queries are compared using:
```
Similarity(Q, D) = (Q · D) / (||Q|| × ||D||)
```
Scores range from 0 (completely different) to 1 (identical meaning).

### Escalation Logic
The agent escalates (routes to human) when:
- **Confidence score < 0.45** — retrieved docs are not relevant enough
- **Sensitive keywords** detected — billing, refund, fraud, duplicate charge, legal
- **3+ consecutive frustrated turns** — unresolved anger signal
- **Zero docs retrieved** — query outside knowledge base scope

### Exponential Backoff
All Gemini API calls implement retry logic:
```python
sleep_time = (2 ** attempt) + random.uniform(0, 1)
```
This handles transient rate limits gracefully.

---

## 📊 Configuration (`src/config.py`)

| Parameter | Default | Description |
|---|---|---|
| `CHUNK_SIZE` | 500 | Characters per document chunk |
| `CHUNK_OVERLAP` | 50 | Overlap between adjacent chunks |
| `TOP_K_RESULTS` | 3 | Number of chunks returned per query |
| `CONFIDENCE_THRESHOLD` | 0.45 | Minimum cosine similarity to avoid escalation |
| `GEMINI_CHAT_MODEL` | `gemini-2.5-flash` | LLM for classification + generation |
| `GEMINI_EMBED_MODEL` | `text-embedding-004` | Embedding model |

---

## 🚢 Deployment

### Option A — Streamlit Community Cloud (Free)
1. Push the repo to GitHub (make sure `.env` is in `.gitignore`)
2. Go to https://share.streamlit.io → New App → select your repo → `app.py`
3. In **Secrets**, add: `GEMINI_API_KEY = "your_key_here"`

### Option B — Railway
```bash
railway init
railway add
railway deploy
```
Set `GEMINI_API_KEY` in Railway → Variables.

---

## 👤 Author

**Bassi**  
Full Stack Development Student | QA Automation Enthusiast  
📧 [your-email@example.com]  
🔗 [LinkedIn](https://linkedin.com/in/your-profile)  
🐙 [GitHub](https://github.com/your-username)

---

## 📄 License

MIT License — free to use, modify, and distribute with attribution.
