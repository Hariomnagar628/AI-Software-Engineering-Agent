# AI-Software-Engineering-Agent
An AI-powered Software Engineering Agent that clones Git repositories, analyzes source code, and answers codebase questions using RAG. Built with Python, FastAPI, Gemini, PostgreSQL, and pgvector, featuring AST-based code analysis, dependency tracking, code embeddings, and semantic search.

# 🤖 AI Software Engineering Agent

An AI-powered Software Engineering Agent that connects Git repositories, analyzes source code, and answers codebase-related questions using Retrieval-Augmented Generation (RAG).

Built with Python, FastAPI, Google Gemini, PostgreSQL, and pgvector.

## 🚀 Features

- **Git Repository Integration:** Clone repositories using HTTPS URLs.
- **Code Analysis:** Extract classes, functions, imports, and function calls using Python AST.
- **Dependency Analysis:** Build function and file dependency graphs.
- **Impact Analysis:** Identify direct and indirect function callers.
- **Code Chunking:** Split source code into manageable chunks.
- **Vector Embeddings:** Generate code embeddings using Google Gemini.
- **Semantic Search:** Find relevant code using PostgreSQL and pgvector.
- **RAG Pipeline:** Retrieve relevant code context and generate AI-powered answers.
- **REST APIs:** Manage repository onboarding, indexing, code analysis, and question answering using FastAPI.

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| Language | Python |
| Backend | FastAPI, Pydantic |
| AI / LLM | Google Gemini |
| Embeddings | Gemini Embedding Model |
| RAG | Custom RAG Pipeline |
| Code Parsing | Python AST |
| Database | PostgreSQL |
| Vector Database | pgvector |
| Git Integration | GitPython |
| Server | Uvicorn |

## 🏗️ Architecture

```text
Git Repository URL
       |
       v
Repository Cloning
       |
       v
File Scanning
       |
       v
Code Analysis (Python AST)
       |
       v
Code Chunking
       |
       v
Gemini Embeddings
       |
       v
PostgreSQL + pgvector
       |
       v
Semantic Search
       |
       v
RAG Retrieval Pipeline
       |
       v
Gemini LLM
       |
       v
AI-Generated Answers
```

## 📁 Project Structure

```text
backend/
├── app/
│   ├── api/
│   │   └── repositories.py
│   ├── core/
│   │   └── database.py
│   ├── models/
│   │   └── code_chunk.py
│   ├── schemas/
│   │   └── repository.py
│   └── services/
│       ├── repository_cloner.py
│       ├── repository_service.py
│       ├── file_scanner.py
│       ├── file_reader.py
│       ├── code_parser.py
│       ├── repository_analyzer.py
│       ├── dependency_resolver.py
│       ├── dependency_graph.py
│       ├── impact_analyzer.py
│       ├── code_chunker.py
│       ├── embedding_service.py
│       ├── vector_store.py
│       ├── semantic_search.py
│       ├── rag_retriever.py
│       ├── llm_service.py
│       ├── prompt_builder.py
│       ├── codebase_qa.py
│       └── repository_onboarding.py
├── tests/
├── .env
└── requirements.txt

workspace/
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd ai-software-engineering-agent
```

### 2. Create a virtual environment

```bash
cd backend

python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file inside the `backend` directory:

```env
GEMINI_API_KEY=your_gemini_api_key

DATABASE_URL=postgresql+psycopg://agent_user:your_password@localhost:5433/agent_db
```

### 5. Start PostgreSQL with pgvector

```bash
docker run \
  --name agent-postgres \
  -e POSTGRES_USER=agent_user \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=agent_db \
  -p 5433:5432 \
  -v agent_postgres_data:/var/lib/postgresql/data \
  -d pgvector/pgvector:pg17
```

Enable the vector extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 6. Start the FastAPI server

```bash
uvicorn app.main:app --reload
```

Open the API documentation:

```text
http://127.0.0.1:8000/docs
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/repositories/clone` | Clone a Git repository |
| POST | `/repositories/onboard` | Clone and index a repository |
| POST | `/repositories/inspect` | Inspect repository details |
| POST | `/repositories/scan` | Scan repository files |
| POST | `/repositories/analyze` | Analyze source code |
| POST | `/repositories/impact` | Analyze function impact |
| POST | `/repositories/search` | Keyword-based code search |
| POST | `/repositories/index` | Index repository code |
| POST | `/repositories/semantic-search` | Search code semantically |
| POST | `/repositories/retrieve` | Retrieve relevant code context |
| POST | `/repositories/ask` | Ask questions about the codebase |

## 💬 Example Usage

### Onboard a Git Repository

**Request:**

```json
{
  "repository_url": "https://github.com/username/project.git"
}
```

### Ask a Question

**Request:**

```json
{
  "path": "/path/to/workspace/project",
  "question": "Explain the authentication flow in this project.",
  "limit": 5
}
```

The agent retrieves relevant code chunks and generates an answer using Gemini.

## 🧪 Run Tests

```bash
pytest -v
```

## 🔐 Security Notes

- Keep API keys and database credentials in environment variables.
- Do not commit `.env` files.
- Only clone repositories you are authorized to access.
- Use isolated execution environments before introducing automated code execution or modification.

## 🛣️ Future Enhancements

- Multi-language code analysis.
- Conversation memory and chat history.
- Incremental repository indexing.
- AI-powered bug investigation.
- Automated code fix suggestions.
- Human-approved code modifications.
- Docker sandbox for test execution.
- React-based frontend dashboard.

## 👨‍💻 Author

Developed as a hands-on project to explore AI agents, software engineering automation, code intelligence, and Retrieval-Augmented Generation.
