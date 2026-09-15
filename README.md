# Enterprise AI Knowledge Agent

**Tech Stack:** Python · FastAPI · LangGraph · OpenAI API · RAG · Hybrid Retrieval · Reranking · Pytest · Docker · GitHub Actions

A production-style enterprise knowledge assistant built with Retrieval-Augmented Generation (RAG), LangGraph, FastAPI, hybrid retrieval, reranking, evaluation, prompt-injection protection, Docker, and automated CI testing.

The project demonstrates how to build a source-grounded AI assistant that retrieves relevant enterprise knowledge, reranks candidate documents, generates cited responses, and applies basic security controls before sending retrieved content to the language model.

---

## Features

- Document ingestion for TXT and PDF files
- Configurable text chunking with overlap
- OpenAI embeddings using `text-embedding-3-small`
- Semantic vector retrieval
- Keyword-based lexical retrieval
- Hybrid retrieval combining semantic and keyword scores
- Retrieval reranking
- Source-grounded answer generation
- Source citations such as `[Source 1]`
- LangGraph-based RAG workflow orchestration
- FastAPI REST API
- Prompt-injection detection for retrieved content
- Automated retrieval and groundedness evaluation
- Pytest unit tests
- GitHub Actions CI
- Docker containerization

---

## Architecture

```text
                    User Question
                         |
                         v
                  +--------------+
                  |   FastAPI    |
                  +--------------+
                         |
                         v
                 +----------------+
                 |   LangGraph    |
                 |   Workflow     |
                 +----------------+
                         |
                         v
                 +----------------+
                 | Hybrid Search  |
                 +----------------+
                   /            \
                  v              v
        +----------------+   +----------------+
        | Semantic Search|   | Keyword Search |
        +----------------+   +----------------+
                   \            /
                    v          v
                    +----------+
                         |
                         v
                  +--------------+
                  |  Reranking   |
                  +--------------+
                         |
                         v
                +------------------+
                | Security Filter  |
                | Prompt Injection |
                +------------------+
                         |
                         v
                +------------------+
                | Context Builder  |
                +------------------+
                         |
                         v
                 +---------------+
                 | OpenAI Model  |
                 +---------------+
                         |
                         v
              Grounded Answer + Sources
```

---

## LangGraph Workflow

The RAG pipeline is orchestrated as a LangGraph state graph:

```text
retrieve
   |
   v
rerank
   |
   v
answer
   |
   v
 END
```

The workflow passes a shared state containing the query, retrieved documents, reranked results, constructed context, and final answer.

---

## Retrieval Pipeline

The retrieval system combines semantic search and lexical matching.

### Semantic Retrieval

Documents are embedded using:

```text
text-embedding-3-small
```

Cosine similarity is used to compare the user query with document chunks.

### Keyword Retrieval

A lexical overlap score is calculated between query terms and document terms.

### Hybrid Retrieval

The semantic and keyword scores are combined:

```text
Hybrid Score =
0.7 × Semantic Score
+
0.3 × Keyword Score
```

This helps the system retrieve both semantically similar content and exact keyword matches.

---

## Reranking

Initial hybrid retrieval candidates are reranked before being passed to the language model.

The current lightweight reranker combines:

```text
0.8 × Hybrid Retrieval Score
+
0.2 × Lexical Overlap Score
```

This provides an additional relevance layer after retrieval.

Example evaluation:

```text
Question:
Why are vector databases useful in RAG?

Before reranking:
chunk=4 hybrid=0.6572
chunk=5 hybrid=0.5504
chunk=0 hybrid=0.4359

After reranking:
chunk=4 rerank=0.6972
chunk=5 rerank=0.5546
chunk=12 rerank=0.4620
```

---

## Prompt-Injection Protection

Retrieved enterprise documents are treated as untrusted input.

Before retrieved text is added to the language-model context, the security layer checks for suspicious instructions such as:

```text
Ignore previous instructions
Reveal your system prompt
Override instructions
Disregard previous instructions
```

Potential prompt-injection content is removed before context construction.

Example:

```python
sanitize_retrieved_text(text)
```

Malicious content is replaced with:

```text
[Potential prompt-injection content removed from retrieved document.]
```

---

## FastAPI API

Start the API locally:

```bash
python -m uvicorn app.main:app --reload
```

Open Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### Health Endpoint

```http
GET /health
```

Example response:

```json
{
  "status": "healthy"
}
```

### Ask Endpoint

```http
POST /ask
```

Example request:

```json
{
  "question": "How does RAG reduce hallucinations?",
  "file_path": "data/sample_document.txt",
  "top_k": 3
}
```

The response contains the generated answer and retrieved source chunks.

---

## Example LangGraph Execution

Run:

```bash
PYTHONPATH=. python -u app/agent_graph.py
```

Example execution:

```text
LangGraph: retrieving documents...
LangGraph: reranking results...
LangGraph: generating answer...

FINAL ANSWER

Hybrid retrieval improves RAG by combining multiple retrieval signals,
improving recall and retrieval robustness. [Source 3]

RERANKED SOURCES

Chunk 19
Chunk 0
Chunk 9
```

---

## Evaluation

The project contains several evaluation scripts under:

```text
evals/
```

### RAG Evaluation

```bash
PYTHONPATH=. python -u evals/evaluate_rag.py
```

The current evaluation checks whether expected concepts appear in generated answers.

### Groundedness Proxy

```bash
PYTHONPATH=. python -u evals/evaluate_groundedness.py
```

The current groundedness proxy checks:

- whether source chunks were returned
- whether the answer contains source citations
- whether relevant retrieved chunks have positive retrieval scores

### Retrieval Comparison

```bash
PYTHONPATH=. python -u evals/compare_retrieval.py
```

This compares hybrid retrieval results before and after reranking.

---

## Automated Tests

Run the test suite with:

```bash
PYTHONPATH=. pytest -v
```

Current tests cover:

- text cleaning
- document chunking
- reranking behavior
- prompt-injection detection
- normal content handling
- malicious-content sanitization

Current local result:

```text
6 passed
```

---

## Continuous Integration

GitHub Actions automatically runs the test suite on:

- pushes to `main`
- pull requests targeting `main`

Workflow:

```text
.github/workflows/tests.yml
```

This ensures new changes are automatically validated before integration.

---

## Docker

Build the Docker image:

```bash
docker build -t enterprise-ai-knowledge-agent .
```

Run the container:

```bash
docker run \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_api_key \
  enterprise-ai-knowledge-agent
```

The API will be available at:

```text
http://localhost:8000
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Rishika73/enterprise-ai-knowledge-agent.git
cd enterprise-ai-knowledge-agent
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

---

## Environment Variables

Create a local `.env` file:

```text
OPENAI_API_KEY=your_openai_api_key_here
```

Do not commit the `.env` file.

The repository includes:

```text
.env.example
```

as a configuration template.

---

## Project Structure

```text
enterprise-ai-knowledge-agent/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── app/
│   ├── agent_graph.py
│   ├── hybrid_retriever.py
│   ├── ingest.py
│   ├── main.py
│   ├── rag.py
│   ├── reranker.py
│   ├── retriever.py
│   ├── security.py
│   └── vector_store.py
│
├── data/
│   └── sample_document.txt
│
├── docs/
│   └── rag_api_success.png
│
├── evals/
│   ├── compare_retrieval.py
│   ├── evaluate_groundedness.py
│   ├── evaluate_rag.py
│   ├── groundedness_results.txt
│   ├── reranking_results.txt
│   └── results.txt
│
├── tests/
│   ├── test_ingest.py
│   ├── test_reranker.py
│   └── test_security.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Technology Stack

### AI / LLM

- OpenAI API
- Retrieval-Augmented Generation
- LangGraph
- Embeddings

### Backend

- Python
- FastAPI
- Uvicorn

### Retrieval

- Semantic search
- Keyword search
- Hybrid retrieval
- Cosine similarity
- Reranking

### Security

- Prompt-injection detection
- Retrieved-content sanitization

### Testing / DevOps

- Pytest
- GitHub Actions
- Docker

---

## Design Goals

This project focuses on several challenges commonly encountered when deploying enterprise AI assistants:

- grounding LLM responses in enterprise knowledge
- reducing hallucinations
- combining multiple retrieval strategies
- reranking candidate documents
- returning source-backed responses
- protecting the model from malicious retrieved instructions
- exposing the system through an API
- evaluating retrieval and answer behavior
- building a reproducible deployment environment
- automatically testing changes through CI

---

## Future Improvements

Potential future extensions include:

- persistent vector database integration
- authentication and document-level access control
- conversation memory
- improved cross-encoder or LLM-based reranking
- retrieval caching
- latency and token-cost observability
- tracing
- stronger prompt-injection classification
- multi-document ingestion
- asynchronous API processing
- production deployment

---
