# 🤖 AI Customer Support Bot

> A production-structured RAG (Retrieval Augmented Generation) API that answers customer questions using your own knowledge base — powered by LLaMA 3.3, pgvector, and FastAPI.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green?style=flat-square&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL+pgvector-blue?style=flat-square&logo=postgresql)
![LLaMA](https://img.shields.io/badge/LLM-LLaMA%203.3%2070B-orange?style=flat-square)
![Embeddings](https://img.shields.io/badge/Embeddings-sentence--transformers-red?style=flat-square)

---

## 🎯 The Problem This Solves

Generic LLMs don't know your business. Ask ChatGPT your refund policy — it hallucinates.

This system ingests **your** documents, converts them into semantic vectors, and answers questions using only your knowledge base. No hallucinations. Every answer is grounded in your actual content and cites its sources.

```
User: "How do I get a refund?"

❌ Generic LLM:  "Most companies offer refunds within 30 days..." (made up)

✅ This system:  "You can request a refund within 30 days by emailing
                  support@company.com with your order number. Refunds
                  process in 5-7 business days."
                  
                  Sources: Refund Policy (relevance: 0.923) ← cited!
                  Confidence: high
```

---

## ✨ Features

- **RAG Pipeline** — Retrieve → Augment → Generate. Industry-standard pattern powering Notion AI, GitHub Copilot, and every modern AI product
- **Local embeddings** — `sentence-transformers` runs fully offline. No API calls, no rate limits, ~10ms latency
- **pgvector similarity search** — cosine distance search inside PostgreSQL. No separate vector DB infra needed
- **Hallucination guard** — LLM is instructed to answer only from provided context. Out-of-scope questions get flagged, not fabricated
- **Source attribution** — every answer returns which documents it used and their relevance scores
- **Confidence scoring** — `high / medium / low` based on similarity score of retrieved documents
- **Bulk ingestion** — ingest entire knowledge bases in one API call with batch embedding
- **Category filtering** — scope questions to specific document categories (refund, shipping, account)
- **Auto Swagger UI** — interactive docs at `/docs`, zero config

---

## 🧠 How RAG Works (The Core Concept)

```
                        INGESTION (one time)
                        ─────────────────────
  Your Documents  ──▶  SentenceTransformer  ──▶  384 numbers  ──▶  pgvector
  (text)               (local AI model)          (embeddings)       (PostgreSQL)


                        RETRIEVAL (every question)
                        ──────────────────────────
  User Question  ──▶  SentenceTransformer  ──▶  384 numbers
                                                     │
                                                     ▼
                                         Cosine similarity search
                                         in pgvector (PostgreSQL)
                                                     │
                                                     ▼
                                         Top 3 matching documents
                                                     │
                                                     ▼
                               Inject docs into LLM prompt
                                                     │
                                                     ▼
                                    LLaMA 3.3 generates answer
                                    using ONLY your content
                                                     │
                                                     ▼
                               Answer + Sources + Confidence
```

**The key insight:** Similar meaning = similar numbers. "Refund" and "money back" produce nearly identical vectors. That's why semantic search finds relevant content even when exact words don't match.

---

## 📡 API Reference

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/documents/ingest` | Ingest a single document |
| `POST` | `/documents/ingest/bulk` | Batch ingest multiple documents |
| `GET` | `/documents/` | List all ingested documents |

**Bulk ingest — example:**
```json
POST /documents/ingest/bulk
{
  "documents": [
    {
      "title": "Refund Policy",
      "category": "refund",
      "content": "We offer a 30-day money-back guarantee..."
    },
    {
      "title": "Shipping Information",
      "category": "shipping",
      "content": "Standard shipping takes 5-7 business days..."
    }
  ]
}
```

```json
{
  "ingested": 2,
  "documents": [
    { "id": "uuid-1", "title": "Refund Policy", "category": "refund", ... },
    { "id": "uuid-2", "title": "Shipping Information", "category": "shipping", ... }
  ]
}
```

---

### Support Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/support/ask` | Ask a question against your knowledge base |

**Ask a question — example:**
```json
POST /support/ask
{
  "question": "How long does shipping take?",
  "category": "shipping"
}
```

```json
{
  "answer": "Standard shipping takes 5-7 business days. Express shipping takes 2-3 business days. Orders placed before 2pm EST ship the same day.",
  "sources": [
    {
      "title": "Shipping Information",
      "category": "shipping",
      "relevance_score": 0.934
    }
  ],
  "confidence": "high"
}
```

**Out-of-scope question (hallucination guard):**
```json
POST /support/ask
{ "question": "What is the capital of France?" }
```
```json
{
  "answer": "I don't have information about that — please contact our support team.",
  "sources": [],
  "confidence": "low"
}
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      FastAPI App                        │
│                                                         │
│  ┌─────────────────┐      ┌──────────────────────────┐  │
│  │ Documents Router│      │    Support Router        │  │
│  │                 │      │                          │  │
│  │ POST /ingest    │      │    POST /ask             │  │
│  │ POST /ingest    │      │                          │  │
│  │       /bulk     │      └────────────┬─────────────┘  │
│  └───────┬─────────┘                   │                │
│          │                             │                │
│          ▼                             ▼                │
│  ┌───────────────┐          ┌──────────────────────┐   │
│  │  Embeddings   │          │     RAG Service      │   │
│  │  Service      │          │                      │   │
│  │               │          │  1. Embed question   │   │
│  │  SentenceTrans│          │  2. Vector search    │   │
│  │  former       │          │  3. Build context    │   │
│  │  (local/offline│         │  4. LLM generation   │   │
│  └───────┬───────┘          └──────────┬───────────┘   │
│          │                             │                │
└──────────┼─────────────────────────────┼────────────────┘
           │                             │
           ▼                             ▼
  ┌─────────────────┐          ┌─────────────────────┐
  │   PostgreSQL    │          │    Groq API          │
  │   + pgvector   │          │    LLaMA 3.3 70B     │
  │                 │          │                      │
  │  documents      │          │  Generates natural   │
  │  ├── content    │          │  language answer     │
  │  ├── embedding  │◀─search──│  from context        │
  │  └── category   │          │                      │
  └─────────────────┘          └─────────────────────┘
```

**Key design decisions:**

- **Local embeddings over API** — `sentence-transformers` runs on-device. Zero latency, zero cost, zero rate limits. Embedding calls go from 200-500ms (API) to ~10ms (local).
- **pgvector over dedicated vector DB** — keeps the stack simple. No Pinecone, no Weaviate, no new infra. PostgreSQL handles both relational data and vector similarity search. One DB to operate.
- **Cosine similarity** — measures angle between vectors, not distance. Scale-invariant — a short FAQ and a long policy doc are compared fairly regardless of length.
- **Hallucination guard via system prompt** — LLM is explicitly told to answer only from provided context and to admit when it doesn't know. Confidence score provides an additional signal.

---

## 🗂️ Project Structure

```
ai-customer-support-bot/
├── main.py                    # App entry, router registration, DB + extension init
├── database.py                # Engine, pgvector extension setup, session management
├── models/
│   ├── __init__.py
│   └── document.py            # SQLAlchemy model with Vector(384) column
├── schemas/
│   ├── __init__.py
│   ├── document.py            # Ingest request/response schemas
│   └── chat.py                # Support request/response + source schemas
├── routers/
│   ├── __init__.py
│   ├── documents.py           # Ingest + list endpoints
│   └── support.py             # RAG chat endpoint
├── services/
│   ├── __init__.py
│   ├── embeddings.py          # Local sentence-transformer embedding
│   ├── retrieval.py           # pgvector cosine similarity search
│   └── rag.py                 # Full RAG pipeline orchestration
├── data/
│   └── sample_faqs.json       # Sample knowledge base for testing
├── create_tables.py           # One-time DB setup script
├── .env.example
└── .gitignore
```

---

## 🧠 Technical Highlights

**Vector storage with pgvector**
```python
# SQLAlchemy model — stores 384-dimensional embedding alongside text
class Document(Base):
    __tablename__ = "documents"
    id        = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content   = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=True)  # ← 384 floats per document
    category  = Column(String, nullable=True)
```

**Cosine similarity search**
```sql
-- pgvector <=> operator = cosine distance
-- 1 - distance = similarity score (higher = more similar)
SELECT id, 1 - (embedding <=> CAST(:embedding AS vector)) AS score
FROM documents
ORDER BY embedding <=> CAST(:embedding AS vector)
LIMIT 3
```

**RAG pipeline — retrieve then generate**
```python
# Step 1: Embed the question locally
question_embedding = get_embedding(question)        # ~10ms, offline

# Step 2: Find semantically similar documents
docs = await find_similar_documents(question, db)   # pgvector search

# Step 3: Inject retrieved context into LLM prompt
prompt = f"Context: {context}\n\nQuestion: {question}"

# Step 4: LLM answers using only provided context
answer = groq_client.chat.completions.create(...)
```

**Confidence scoring**
```python
# Similarity score drives confidence — no guesswork
top_score = docs_with_scores[0][1]
confidence = "high" if top_score > 0.8 else "medium" if top_score > 0.6 else "low"
```

**Batch embedding — efficient ingestion**
```python
# Encode all documents in one model call — not N separate calls
embeddings = model.encode(texts)   # texts = list of all document contents
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- pgvector extension ([install guide](https://github.com/pgvector/pgvector))
- [Groq API key](https://console.groq.com) — free tier, no credit card

### Installation

```bash
git clone https://github.com/yourusername/ai-customer-support-bot
cd ai-customer-support-bot

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup environment
uv venv
source .venv/bin/activate
uv install
```

### Configuration

```bash
cp .env.example .env
```

```bash
# .env
DATABASE_URL=postgresql://localhost/ai_support_bot
GROQ_API_KEY=your_groq_api_key_here
```

### Database Setup

```bash
# Create database
createdb ai_support_bot

# Install pgvector extension (macOS)
brew install pgvector
# or build from source: https://github.com/pgvector/pgvector

# Create tables (run once)
python create_tables.py
```

### Run

```bash
uvicorn main:app --reload
```

Open **http://localhost:8000/docs** ✅

### Seed Knowledge Base

```bash
# Ingest sample FAQs via Swagger UI at /docs
# POST /documents/ingest/bulk with contents of data/sample_faqs.json
```

---

## 🧪 Test Scenarios

| Question | Expected Confidence | Why |
|----------|-------------------|-----|
| "How do I get a refund?" | high (0.9+) | Direct match to Refund Policy |
| "How long does delivery take?" | high (0.9+) | Semantic match to Shipping Info |
| "I forgot my password" | high (0.85+) | Match to Password Reset doc |
| "What is the capital of France?" | low | Not in knowledge base → flagged |

The out-of-scope test is the most important — it proves the hallucination guard works.

---

## 🗺️ Roadmap

- [ ] Streaming responses — SSE token streaming for chat UI
- [ ] Conversation memory — multi-turn support with history
- [ ] Document versioning — update/replace documents without re-ingesting all
- [ ] Hybrid search — combine vector similarity with keyword search (BM25)
- [ ] Auth middleware — API key protection per tenant
- [ ] Admin dashboard — document management UI
- [ ] Docker + docker-compose setup
- [ ] Deploy to Railway / Render

---

## 🔗 Related Projects

Part of an AI-native engineering portfolio built while transitioning from Ruby on Rails → AI Engineering:

| Project | Description | Stack |
|---------|-------------|-------|
| [**ai-native-journey**](https://github.com/yourusername/ai-native-journey) | FastAPI foundation — REST API + AI chat + SSE streaming | FastAPI, PostgreSQL, Groq |
| [**ai-pr-reviewer**](https://github.com/yourusername/ai-pr-reviewer) | AI-powered GitHub PR code reviewer | FastAPI, GitHub API, LLaMA |
| **ai-customer-support-bot** (this) | RAG pipeline — semantic search + grounded answers | FastAPI, pgvector, sentence-transformers |

---

## 👨‍💻 Author

**Kishor Vyavahare**
Senior Software Engineer → AI Native Engineer

11+ years of backend engineering across Ruby on Rails, PostgreSQL, Redis, AWS, and Kubernetes.
Now building production AI systems — RAG pipelines, agentic workflows, and LLM-powered APIs.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat-square&logo=linkedin)](https://linkedin.com/in/vyavahare-kishor)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=flat-square&logo=github)](https://github.com/vyavahare-kishor)

---

## 📄 License

MIT License — use it, fork it, build on it.
