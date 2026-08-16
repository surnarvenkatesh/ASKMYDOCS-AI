# AskMyDocs AI

Enterprise-grade Retrieval-Augmented Generation (RAG) platform. Upload documents (PDF, DOCX, TXT, Markdown), ask questions in natural language, and get cited, hallucination-checked answers backed by a hybrid BM25 + vector retrieval pipeline.

## The Problem

Finding specific information buried in long documents — contracts, reports, research papers, internal wikis, financial filings — is slow and error-prone. Ctrl+F only works if you know the exact wording. Reading the whole document doesn't scale past a handful of files. And generic AI chatbots either can't see your private documents at all, or answer confidently without grounding their response in the actual source text — producing hallucinated facts that are hard to catch without re-reading everything yourself.

## The Solution

AskMyDocs AI lets you upload your own documents and ask questions in plain English. Instead of relying on the model's memory, every answer is generated from content retrieved directly out of your documents using a hybrid BM25 + vector search pipeline, then re-ranked for relevance. Each answer comes with citations back to the source chunks, and a verification step flags when a citation doesn't actually check out — so you can trust the answer or know exactly when to double-check it yourself.

## Use Cases

- **Contracts & legal documents** — quickly find specific clauses, obligations, or terms without reading the whole document
- **Research & academic papers** — ask targeted questions across one or many papers instead of manually searching
- **Financial reports & filings** — pull specific figures, statements, or disclosures on demand
- **Internal knowledge bases** — turn scattered PDFs, policies, and notes into a queryable assistant
- **Resumes / CVs** — quickly extract or verify details across candidate documents
- **Study material** — ask questions against lecture notes, slides, or textbooks while studying


## Stack

| Layer      | Tech |
|------------|------|
| Frontend   | Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, Framer Motion, React Query |
| Backend    | FastAPI, Python 3.12+, SQLAlchemy, Alembic, Pydantic v2 |
| Data       | PostgreSQL, Redis |
| Retrieval  | LangChain, LlamaIndex, FAISS, BM25, Sentence Transformers, Cross-Encoder re-ranking, Reciprocal Rank Fusion |
| LLM        | OpenAI API (optional) or local Ollama |
| Evaluation | RAGAS, DeepEval |

## Project Structure

```
askmydocs-ai/
├── backend/            # FastAPI application
│   ├── app/
│   │   ├── api/v1/         # Route handlers
│   │   ├── core/           # Config, security, logging
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response models
│   │   ├── services/       # Business logic
│   │   ├── repositories/   # Data access layer
│   │   ├── ingestion/      # Document parsing & chunking
│   │   ├── retrieval/      # Hybrid search, RRF, re-ranking
│   │   ├── evaluation/     # RAGAS / DeepEval pipelines
│   │   └── utils/
│   ├── alembic/             # DB migrations
│   └── tests/                # unit / integration / api / evaluation
├── frontend/            # Next.js application
│   └── src/
│       ├── app/            # App Router pages
│       ├── components/     # UI components
│       ├── lib/            # API client, utils
│       ├── hooks/          # Custom React hooks
│       ├── types/          # Shared TypeScript types
│       └── styles/
├── deployment/          # Platform-specific deployment configs
├── docs/                 # Architecture, API, deployment docs
├── .github/workflows/    # CI/CD pipelines
└── docker-compose.yml
```

## Getting Started

```bash
cp .env.example .env         # fill in secrets
docker compose up --build    # starts db, redis, backend, frontend
```

- Backend API: http://localhost:8000 (docs at `/docs`)
- Frontend: http://localhost:3000

See `docs/INSTALLATION.md` for local (non-Docker) setup and `docs/ARCHITECTURE.md` for how the retrieval pipeline works.

## Build Plan

This project is being built incrementally, feature by feature:

1. ✅ Project scaffold & Docker Compose
2. ✅ Backend core: config, auth (JWT), protected routes
3. ✅ Document ingestion: upload, chunking, embeddings, FAISS/BM25 indexing
4. ✅ Hybrid retrieval + RAG chat endpoint (streaming, citations)
4. ✅ Hybrid retrieval + RAG chat endpoint (streaming, citations)
5. ✅ Frontend: landing page → dashboard → chat UI
6. ✅ Analytics, evaluation pipeline, tests, CI/CD, docs

See `docs/API.md`, `docs/ARCHITECTURE.md`, `docs/INSTALLATION.md`, `docs/ENVIRONMENT_VARIABLES.md`, `docs/DEPLOYMENT.md`, and `docs/TROUBLESHOOTING.md` for details on each.

### rag pipeline

```text
                User
                  │
                  ▼
          Next.js Frontend
                  │
                  ▼
             FastAPI API
                  │
                  ▼
          Document Processing
                  │
                  ▼
              Chunking
                  │
                  ▼
            Embeddings
                  │
          ┌───────┴────────┐
          ▼                ▼
        FAISS             BM25
     Vector Search    Keyword Search
          │                │
          └───────┬────────┘
                  ▼
        Reciprocal Rank Fusion
                  │
                  ▼
       Cross-Encoder Reranking
                  │
                  ▼
          Context Selection
                  │
                  ▼
          Prompt Construction
                  │
                  ▼
        Ollama + Llama 3.2
                  │
                  ▼
        Citation Validation
                  │
                  ▼
          Final Response
```

---

# ✨ Key Features

## 📄 Document Intelligence

* PDF document processing
* DOCX document processing
* TXT support
* Markdown support
* Metadata extraction
* Document indexing
* Document management
* Re-indexing support

## 🔎 Hybrid Retrieval

Combines two complementary retrieval strategies:

### BM25

Keyword-based lexical retrieval for:

* Exact terms
* Policy numbers
* Names
* Technical identifiers
* Acronyms
* Error codes

### FAISS

Vector-based semantic retrieval for:

* Meaning-based queries
* Similar concepts
* Natural-language questions
* Semantic relationships

The results are combined using **Reciprocal Rank Fusion (RRF)**.

---

## 🎯 Cross-Encoder Reranking

Initial retrieval can return multiple potentially relevant chunks.

A Cross-Encoder evaluates the relationship between the query and retrieved chunks and assigns relevance scores.

```text
Query
  +
Retrieved Chunk
       │
       ▼
Cross Encoder
       │
       ▼
Relevance Score
```

The highest-quality chunks are then passed to the LLM.

Recommended model:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

---

# 🤖 LLM Generation

The project supports local LLM inference using **Ollama**.

Recommended development model:

```text
Llama 3.2
```

Ollama acts as the local inference runtime, while Llama 3.2 performs the actual natural-language generation.

```text
FastAPI
   │
   ▼
Ollama
   │
   ▼
Llama 3.2
   │
   ▼
Generated Answer
```

The LLM receives the user's question together with the retrieved document context rather than searching the document database itself.

---

# 📚 Retrieval-Augmented Generation Pipeline

The complete pipeline consists of:

### 1. Document Upload

User uploads a document through the web interface.

### 2. Text Extraction

Text is extracted from the document using document-processing libraries.

### 3. Text Cleaning

The extracted text is normalized and cleaned.

### 4. Chunking

Large documents are divided into smaller retrieval units using configurable chunking strategies.

Example:

```text
Chunk Size:     1000
Chunk Overlap:  200
```

### 5. Embedding Generation

Each chunk is converted into a numerical vector using an embedding model.

### 6. Vector Indexing

Embeddings are stored in FAISS for efficient semantic similarity search.

### 7. BM25 Indexing

Document chunks are also indexed using BM25 for lexical retrieval.

### 8. Hybrid Retrieval

BM25 and vector retrieval are combined.

### 9. Reranking

A Cross-Encoder reranks the retrieved candidates.

### 10. Prompt Construction

The highest-quality chunks are inserted into a grounded prompt.

### 11. LLM Generation

Llama 3.2 generates the final response through Ollama.

### 12. Citation Enforcement

The response is linked back to the source document and relevant page/chunk metadata.

---

# 🧠 Tokenization vs Chunking

The system distinguishes between chunking and tokenization.

### Chunking

Splits large documents into manageable retrieval units.

```text
Document
   ↓
Chunk 1
Chunk 2
Chunk 3
```

### Tokenization

Converts text into tokens that models can process.

```text
Text
 ↓
Tokenizer
 ↓
Tokens
```

Token-aware processing can be used to ensure chunks remain within model context limits.

---

# 📌 Citation System

AskMyDocs is designed to provide traceable answers.

A response can include:

```text
Answer:
Employees are entitled to 20 annual leave days.

Source:
Employee_Handbook.pdf

Page:
18

Chunk:
employee_handbook_chunk_42
```

The goal is to reduce unsupported responses and make generated answers auditable.

---

# 📊 RAG Evaluation

The project includes an evaluation pipeline for measuring RAG quality rather than relying only on subjective testing.

Evaluation metrics include:

* Faithfulness
* Answer Relevancy
* Context Recall
* Context Precision
* Retrieval performance
* Response latency

Potential evaluation frameworks:

* RAGAS
* DeepEval
* Custom evaluation scripts

---

# 🧪 Testing

The project includes automated testing for:

* Document processing
* Chunking
* Embedding generation
* Retrieval
* Reranking
* API endpoints
* Authentication
* Citation generation
* RAG responses

Testing tools:

```text
pytest
pytest-asyncio
pytest-cov
```

---

# 🏗️ Architecture

```text
┌──────────────────────────────────────────────┐
│                 Next.js UI                   │
│                                              │
│  Dashboard │ Chat │ Documents │ Analytics   │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│                 FastAPI                      │
│                                              │
│ Authentication │ Documents │ Chat │ Search  │
└──────────────────────┬───────────────────────┘
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
       PostgreSQL              Redis
             │                   │
             └─────────┬─────────┘
                       ▼
┌──────────────────────────────────────────────┐
│              RAG Pipeline                    │
│                                              │
│ Extraction → Chunking → Embeddings           │
│                                              │
│ BM25 ───────────────┐                        │
│                     ├─→ Hybrid Retrieval     │
│ FAISS ──────────────┘                        │
│                       │                      │
│                       ▼                      │
│                Cross Encoder                 │
│                       │                      │
│                       ▼                      │
│                 Prompt Builder               │
│                       │                      │
│                       ▼                      │
│               Ollama / Llama 3.2            │
│                       │                      │
│                       ▼                      │
│              Citation Validation             │
└──────────────────────────────────────────────┘
```

---



### getting started

# 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>

cd askmydocs-ai
```

---

# 2. Configure Backend

```bash
cd backend
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 3. Configure Environment Variables

Create:

```text
.env
```

Example:

```env
APP_ENV=development

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/askmydocs

REDIS_URL=redis://localhost:6379

OLLAMA_BASE_URL=http://localhost:11434

OLLAMA_MODEL=llama3.2

SECRET_KEY=change-this-in-production
```

Never commit real API keys, passwords, or secrets.

---

# 4. Start Ollama

Start the Ollama service:

```bash
ollama serve
```

In another terminal, download the model:

```bash
ollama pull llama3.2
```

Test it:

```bash
ollama run llama3.2
```

---

# 5. Start Database Services

If Docker Compose is configured:

```bash
docker compose up -d postgres redis
```

Check running containers:

```bash
docker compose ps
```

---

# 6. Run Database Migrations

```bash
cd backend

alembic upgrade head
```

---

# 7. Start FastAPI

From the backend directory:

```bash
uvicorn app.main:app --reload --port 8000
```

API:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

---

# 8. Start Frontend

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start development server:

```bash
npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

# 🐳 Docker Setup

The project can be run using Docker Compose.

```bash
docker compose up --build
```

Stop services:

```bash
docker compose down
```

---

# 🔐 Security

The application is designed with security considerations including:

* JWT authentication
* Password hashing
* Environment-based secrets
* File type validation
* File size limits
* API validation
* Protected routes
* Rate limiting
* CORS configuration

Production deployments should additionally use HTTPS, secure secret management, network restrictions, and appropriate access controls.

---
# 📈 Future Improvements

Planned enhancements include:

* [ ] Streaming LLM responses
* [ ] Multi-user workspaces
* [ ] Role-Based Access Control
* [ ] Multi-document conversations
* [ ] Advanced metadata filtering
* [ ] Semantic chunking
* [ ] Parent-child retrieval
* [ ] Query rewriting
* [ ] HyDE retrieval
* [ ] Hybrid reranking improvements
* [ ] Qdrant/Weaviate integration
* [ ] Observability with OpenTelemetry
* [ ] Prometheus metrics
* [ ] Cloud deployment
* [ ] Automated benchmark datasets
* [ ] Model comparison dashboard

---

# 🎯 Why This Project?

AskMyDocs demonstrates practical AI Engineering concepts beyond simply calling an LLM API.

The project covers:

```text
LLM Engineering
        +
Information Retrieval
        +
Vector Search
        +
Hybrid Search
        +
Reranking
        +
Prompt Engineering
        +
Evaluation
        +
Backend Engineering
        +
Frontend Engineering
        +
DevOps
```

It is designed to demonstrate how modern RAG systems can be built with production-oriented engineering practices.

---



# 🧪 Example Query

**User:**

> What is the company's annual leave policy?

**Retrieval:**

```text
BM25
  +
FAISS
  ↓
Hybrid Results
  ↓
Cross-Encoder
```

**Context:**

```text
Employees are entitled to 20 annual leave
days per calendar year.
```

**LLM:**

```text
Llama 3.2
```

**Response:**

> Employees are entitled to 20 annual leave days per calendar year.

**Citation:**

```text
Source: Employee_Handbook.pdf
Page: 18
```

---


# 🤝 Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature/your-feature
```

3. Make your changes.
4. Add tests.
5. Run the test suite.

```bash
pytest
```

6. Commit your changes.

```bash
git commit -m "feat: add your feature"
```

7. Push the branch.

```bash
git push origin feature/your-feature
```

8. Open a Pull Request.
---

# 👨‍💻 Author

**Venkatesh Surnar**

B.Tech Computer Science Engineering

AI / ML Engineer | Generative AI | RAG | Machine Learning

---

> **AskMyDocs AI — Turning documents into an intelligent, searchable knowledge base.**
