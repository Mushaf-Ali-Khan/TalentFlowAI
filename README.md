# TalentFlowAI — AI-Powered Recruitment Intelligence Platform

TalentFlowAI is a state-of-the-art, full-stack recruitment intelligence platform designed to automate and streamline the candidate screening process. By leveraging a multi-agent AI pipeline, semantic vector embeddings, explainable scoring, bias auditing, and automated recruiter workflows, it turns raw CV uploads (PDF/DOCX) into structured, ranked, and actionable shortlists.

Developed as a Final Year Project (FYP) and startup prototype, TalentFlowAI delivers premium, real-time recruiting intelligence under a sleek, dark-mode glassmorphic user interface.

---

## 1. High-Level System Architecture

```mermaid
graph TD
    A[Next.js Frontend] -->|REST API| B(FastAPI Backend)
    B -->|JWT Auth| C[Clerk Auth Provider]
    B -->|Async Tasks| D[Celery + Redis]
    D -->|LangGraph| E{AI Screening Agent}
    E -->|Primary LLM| F[Claude 3.5 Sonnet]
    E -->|Fallback LLM| G[Ollama Qwen2.5]
    E -->|Embeddings| H[BAAI bge-m3]
    B -->|Vector Search| I[(PostgreSQL + pgvector)]
    B -->|File Storage| J[(S3 Storage)]
```

---

## 2. Core Platform Features

### 📂 Multi-Format Resume Ingestion
* **Parser Engine:** Handles standard `PDF` and Word (`DOCX`) files, implementing a multi-stage fallback strategy (pdfplumber → PyMuPDF → OCR placeholder).
* **Experience Parsing & Deduplication:** Parses chronological employment history, filters overlapping periods using date-range deduplication logic, and robustly handles corrupted character sets (e.g., Unicode artifacts like `\ufffd` or custom page-break dashes).

### 🤖 Multi-Node AI screening Agent Pipeline (LangGraph)
The background processing pipeline runs on **Celery** workers executing a 7-node **LangGraph** orchestration graph:
1. **ParserNode:** Extracts raw text from uploaded binary files.
2. **ExtractorNode:** Structures raw text into a standard Pydantic schema using structured Claude 3.5 Sonnet / Ollama prompts. Automatically computes total experience, skills, and seniority level.
3. **EmbedderNode:** Generates a 1024-dimensional semantic embedding from the parsed profile using the `BAAI/bge-m3` model.
4. **MatcherNode:** Performs pgvector cosine-similarity searches against the job description's embedding. Rejects candidates failing the minimum match score (e.g., `0.20`).
5. **ScorerNode:** Scores the candidate across 4 dimensions: **Skills Alignment**, **Experience Match**, **Education & Credentials**, and **Growth Potential**.
6. **BiasAuditNode:** Scours profiles for demographic bias indicators (gender pronouns, names, locations, age proxies) and logs findings to an isolated database for transparency.
7. **PersistNode:** Commits candidate scores, structured profile data, vector embeddings, and audit logs to the database in a single database transaction.

### ⚡ Real-World Auto-Shortlisting Workflow
* Automatically transitions processed candidates with a total screening score ≥ `AUTO_SHORTLIST_THRESHOLD` (default: **`75.0`**) to a `shortlisted` status.
* Candidates failing the threshold remain in the pipeline for manual recruiter review.

### 📅 Recruiter Dashboard & Interview Scheduler
* Interactive dashboard listing active jobs, candidate counts, and status breakdowns.
* Ranked candidate leaderboards with animated color-coded scoring circles.
* Detail slide-overs highlighting AI-reasoned scoring justifications and full profile JSON specs.
* Dedicated interview scheduling panel to easily manage meetings (formats, dates, links) with email notifications.

---

## 3. Technology Stack & Dependencies

### Backend
* **Runtime:** Python ≥ 3.12
* **Web Framework:** FastAPI (0.115.6)
* **ASGI Server:** Uvicorn (≥ 0.30.0)
* **AI Orchestration:** LangGraph (0.3.21)
* **LLM APIs:** langchain-anthropic (0.3.10)
* **Local Fallback:** Ollama (Qwen2.5:14b)
* **Embeddings:** BAAI/bge-m3 via sentence-transformers (3.3.1)
* **Task Queuing:** Celery (5.4.0) + Redis (5.2.1)
* **Database & Vector Search:** PostgreSQL 16 + pgvector (0.3.6) + SQLAlchemy (2.0.36)

### Frontend
* **Framework:** Next.js 15.5.18 (Turbopack-enabled)
* **UI Library:** React 19.1.0
* **Styling:** Tailwind CSS v4 (Dark Glassmorphic UI)
* **Auth Component:** Clerk Next.js SDK
* **State Management:** Zustand (5.0.13) + React Query (5.100.10)

---

## 4. Getting Started: Installation & Run Guide

### 4.1 Prerequisites
Ensure the following tools are installed on your machine:
* [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* [Python 3.12+](https://www.python.org/downloads/)
* [Node.js 20+](https://nodejs.org/)
* [Git](https://git-scm.com/)

---

### 4.2 Step 1: Clone the Repository
```bash
git clone https://github.com/Mushaf-Ali-Khan/TalentFlowAI.git
cd TalentFlowAI
```

---

### 4.3 Step 2: Spin Up Infrastructure Services (Docker)
In the root directory of the project, run:
```bash
docker-compose up -d
```
This launches:
* **PostgreSQL + pgvector** (Port `5432`)
* **Redis** (Port `6379`)

---

### 4.4 Step 3: Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd talentflow-backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create your local environment configuration file:
   Copy `.env.example` or create a new file named `.env.local` with the following variables:
   ```env
   # PostgreSQL Connection
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/talentflow
   DATABASE_SYNC_URL=postgresql://postgres:postgres@localhost:5432/talentflow
   
   # Redis Broker for Celery
   REDIS_URL=redis://localhost:6379/0
   
   # LLM API Config
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   OLLAMA_BASE_URL=http://localhost:11434
   
   # Vector Embedding Setup
   EMBEDDING_MODEL_NAME=BAAI/bge-m3
   
   # Screening Rules
   AUTO_REJECT_THRESHOLD=20.0
   AUTO_SHORTLIST_THRESHOLD=75.0
   
   # Clerk Authentication Keys (Keyless dev mode bypasses if empty)
   CLERK_SECRET_KEY=your_clerk_secret_key
   CLERK_JWKS_URL=your_clerk_jwks_url
   ```
5. Run the database migrations using Alembic:
   ```bash
   alembic upgrade head
   ```
6. Create the default mock organization (required for local development auth bypass):
   ```bash
   python create_default_org.py
   ```
7. Start the FastAPI backend server:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
8. In a **new terminal tab** (with environment activated), launch the Celery background worker:
   ```bash
   # Windows (requires thread pool):
   celery -A app.workers.celery_app worker --loglevel=info --pool=threads --concurrency=4
   # macOS/Linux:
   celery -A app.workers.celery_app worker --loglevel=info
   ```

---

### 4.5 Step 4: Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd ../talentflow-frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Create your environment variable file `.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   
   # Clerk Authentication
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
   CLERK_SECRET_KEY=sk_test_...
   ```
   > ⚠️ **Security Note:** Never commit your `.env.local` files to version control. They are ignored by default via `.gitignore`.
4. Run the Next.js development server:
   ```bash
   npm run dev
   ```
5. Open your browser and navigate to [http://localhost:3000](http://localhost:3000).

---

### 4.6 Verification & Seeding
To verify your installation and seed dummy jobs/candidates for testing, we've included testing and parsing scripts inside `talentflow-backend`:
* **Run E2E Pipeline Integration Test:**
  ```bash
  python e2e_test.py
  ```
* **Verify database connection and entries:**
  ```bash
  python check_db.py
  ```

---

## 5. Testing and Validation
* **Unit & E2E Testing:** Executed via `pytest` and `e2e_test.py` simulation.
* **Fallback Verification:** The Anthropic circuit breaker can be validated by disabling the network or passing an invalid API key, routing requests to Ollama seamlessly.
* **Auto-Shortlist Verification:** Candidate scores above the set threshold (e.g. `75.0`) will immediately display a `shortlisted` badge under the candidate table and count statistics.
