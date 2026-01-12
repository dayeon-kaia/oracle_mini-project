# ML Service - Flask RAG Backend

This is a Flask-based RAG (Retrieval-Augmented Generation) service for the EDCC dashboard.

## Features

- **RAG Search** (`/search`): Semantic search over medical guidelines
- **Protocol Generation** (`/protocol`): LLM-powered protocol recommendations based on RAG
- **Clinical Summary** (`/api/clinical-summary`): AI-generated clinical summaries for medical staff
- **Gentle Report** (`/api/gentle-report`): Patient-friendly reports for families
- **Query Parsing** (`/api/query`): Natural language query interpretation
- **Rule Engine** (`/api/evaluate-protocols`): Rule-based protocol evaluation

## Prerequisites

- Python 3.13+
- ChromaDB vector database (included in `db_medical_md`)
- Medical guidelines PDFs (included in `guidelines`)
- OpenAI API key (optional, for LLM features)

## Setup

1. **Create virtual environment**:
```bash
python3 -m venv venv
```

2. **Install dependencies**:
```bash
./venv/bin/pip install -r requirements.txt
```

3. **Configure environment**:
Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

4. **Start the server**:
```bash
./venv/bin/python app.py
```

The server will start on port 5003.

## API Endpoints

### RAG Endpoints

- `POST /search` - Semantic search
- `POST /protocol` - Generate protocol with evidence

### LLM Endpoints

- `POST /api/clinical-summary` - Generate clinical summary
- `POST /api/gentle-report` - Generate patient report
- `POST /api/query` - Parse natural language query

### Rule Engine

- `POST /api/evaluate-protocols` - Evaluate rule-based protocols

## Frontend Integration

The frontend (running on port 5173) connects to this service for:
- Protocol Guide in AISupportHub
- Clinical Explain in AISupportHub
- AI Search in TopCommandBar

## Architecture

```
ml-service/
├── app.py                 # Flask application
├── rag_markdown.py        # RAG vector store builder
├── clinical_summary.py    # Clinical summary generator
├── gentle_report.py       # Gentle report generator
├── qa_interface.py        # Query parsing interface
├── rule_engine.py         # Rule-based protocol engine
├── llm_service.py         # LLM service wrapper
├── db_medical_md/         # ChromaDB vector store
├── guidelines/            # Medical guideline PDFs
└── protocols/             # JSON rule definitions
```

## Notes

- CORS is enabled for frontend integration
- Vector database is pre-built from markdown-chunked PDFs
- LLM features require OpenAI API key
- RAG search works without API key using local embeddings (BAAI/bge-m3)
