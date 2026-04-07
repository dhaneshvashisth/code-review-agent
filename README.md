# Code Review Agent

A production-grade multi-agent AI system that performs automated code reviews using LangGraph, LangChain, and OpenAI GPT-4o-mini. Submit code and receive a structured review report covering bugs, code quality, and security vulnerabilities — all analyzed in parallel by specialized AI agents.

---

## Architecture

```
POST /api/v1/review
        ↓
  [Orchestrator Agent]
  Validates input, checks cache, routes graph
        ↓ (parallel execution)
  ┌─────────────────────────────────────────┐
  │  Bug Detector  │  Quality  │  Security  │
  └─────────────────────────────────────────┘
        ↓ (converge)
  [Summarizer Agent]
  Combines findings, calculates score, writes summary
        ↓
  [PostgreSQL]
  Persists all results for history and caching
        ↓
  JSON Response
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI Orchestration | LangGraph, LangChain |
| LLM | OpenAI GPT-4o-mini |
| Backend | FastAPI, Python 3.11 |
| Database | PostgreSQL 18, SQLAlchemy (async), asyncpg |
| Reliability | Tenacity (retry logic), Pydantic (validation) |
| Infrastructure | Docker, Docker Compose |

---

## Features

- **Multi-agent parallel execution** — 3 specialized agents run simultaneously, reducing review time by ~66%
- **Intelligent caching** — SHA256 hash deduplication returns cached results instantly without LLM calls
- **Graceful failure handling** — partial reviews returned when individual agents fail, system never crashes
- **Full persistence** — every review, agent output, and error saved to PostgreSQL
- **Production-ready API** — versioned endpoints, request ID tracking, CORS, input validation, pagination

---

## Agents

| Agent | Responsibility |
|---|---|
| Orchestrator | Input validation, cache check, graph routing |
| Bug Detector | Logical errors, edge cases, unhandled exceptions, runtime failures |
| Quality Checker | Readability, naming conventions, complexity, code smells, best practices |
| Security Checker | Hardcoded secrets, SQL injection, unsafe eval(), exposed sensitive data |
| Summarizer | Combines all findings, calculates score, generates executive summary |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/review` | Submit code for review |
| GET | `/api/v1/review/{review_id}` | Fetch a specific past review |
| GET | `/api/v1/history` | Paginated list of all past reviews |
| GET | `/api/v1/health` | Health check |

---

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/code-review-agent.git
cd code-review-agent
```

### 2. Set up environment

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```
OPENAI_API_KEY=your_openai_api_key_here
POSTGRES_PASSWORD=yourpassword
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@postgres:5432/code_review_db
```

### 3. Run with Docker

```bash
docker-compose up --build
```

### 4. Test the API

Open interactive API docs:
```
http://localhost:8000/docs
```

### 5. View database (optional)

```
http://localhost:5050
Email:    admin@admin.com
Password: admin
Host:     postgres
Port:     5432
```

---

## Sample Request

```bash
POST /api/v1/review
Content-Type: application/json

{
  "code": "password = 'admin123'\nquery = 'SELECT * FROM users WHERE id = ' + user_input\neval(query)",
  "language": "python"
}
```

## Sample Response

```json
{
  "status": "completed",
  "message": "Review completed successfully",
  "review_id": "3c907faa-7f01-459d-a016-5343058190f9",
  "cached": false,
  "final_report": {
    "overall_score": 14,
    "critical_issues": 5,
    "warnings": 2,
    "total_findings": 8,
    "failed_agents": [],
    "partial_review": false,
    "summary": "The code exhibits critical vulnerabilities including hardcoded passwords, SQL injection risk, and unsafe use of eval(). Immediate remediation is required before this code can be considered production-ready.",
    "findings": [
      {
        "type": "security",
        "severity": "critical",
        "message": "Hardcoded password found in the code.",
        "line": 1
      },
      {
        "type": "security",
        "severity": "critical",
        "message": "SQL injection vulnerability due to unsanitized user input.",
        "line": 2
      },
      {
        "type": "security",
        "severity": "critical",
        "message": "Unsafe use of eval() which can execute arbitrary code.",
        "line": 3
      }
    ]
  }
}
```

---

## Project Structure

```
code-review-agent/
├── app/
│   ├── agents/
│   │   ├── orchestrator.py      # Entry point, validates input, checks cache
│   │   ├── bug_detector.py      # Finds bugs and logical errors
│   │   ├── quality_checker.py   # Checks code quality and best practices
│   │   ├── security_checker.py  # Detects security vulnerabilities
│   │   └── summarizer.py        # Combines findings, generates report
│   ├── graph/
│   │   ├── state.py             # LangGraph shared state definition
│   │   └── graph.py             # Graph nodes, edges, parallel execution
│   ├── api/
│   │   ├── routes.py            # FastAPI route handlers
│   │   └── schemas.py           # Pydantic request/response schemas
│   ├── db/
│   │   ├── models.py            # SQLAlchemy models (4 tables)
│   │   ├── database.py          # Async engine, session factory
│   │   └── crud.py              # All database operations
│   ├── core/
│   │   ├── config.py            # pydantic-settings environment config
│   │   ├── llm.py               # Shared LLM client with retry logic
│   │   └── exceptions.py        # Custom exception classes
│   └── main.py                  # FastAPI app, middleware, lifespan
├── tests/
├── docker-compose.yml
├── Dockerfile
├── .env.example
└── requirements.txt
```

---

## Database Schema

| Table | Purpose |
|---|---|
| `review_requests` | Every code submission — hash, language, status |
| `agent_outputs` | Individual agent findings per review |
| `final_reports` | Combined final report with score and summary |
| `error_logs` | All system errors with full context and timestamps |

---

## How Caching Works

Every submitted code is SHA256 hashed before any LLM calls. If the same code was reviewed before, the cached result is returned immediately — no API calls, no cost, instant response.

```
Submit code
    ↓
Hash code → check PostgreSQL
    ↓
Cache hit?  → Return cached report instantly
Cache miss? → Run all agents → Save to DB → Return report
```

---

## How Failure Handling Works

Each agent handles its own failures independently:
- LLM timeout → retry up to 3 times with exponential backoff
- Agent still fails → marks itself as failed, returns empty findings
- Summarizer detects failed agents → marks review as partial
- All agents fail → returns minimal report with clear error message
- Database error → review marked as FAILED, error logged

The system always returns a meaningful response — never a raw crash.

---

## Supported Languages

`python` `javascript` `typescript` `java` `go` `rust` `cpp` `c` `csharp` `ruby` `php` `swift`

---

## Environment Variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `DATABASE_URL` | PostgreSQL async connection string |
| `POSTGRES_USER` | PostgreSQL username |
| `POSTGRES_PASSWORD` | PostgreSQL password |
| `POSTGRES_DB` | Database name |
| `APP_ENV` | `development` or `production` |
| `DEBUG` | `True` or `False` |