# Question Bank

Question Bank is a document question-and-answer application. A user uploads a
PDF, the backend splits and indexes its text, and the chat interface answers
questions using relevant passages from that document. When the document does
not contain an answer, the current backend can fall back to web search.

The current scope is document Q&A. The planned next product capability is
question-bank generation, with broader support for finding, ingesting, and
explaining college documents treated as a future direction rather than part of
the current milestone. Supabase Auth is the planned authentication service.

The application is currently a portfolio prototype. Sessions and chat history
are held in memory, vectors are stored in a local Chroma database, and uploaded
PDFs are processed synchronously. See [ROADMAP.md](ROADMAP.md) for the work
planned to make the project durable and production-ready.

## Project structure

```text
QuestionBank/
|-- backend/              FastAPI API, PDF ingestion, retrieval, and AI agent
|-- frontend/             React and Vite web interface
|-- README.md             Project and local-development documentation
`-- ROADMAP.md            Planned engineering milestones
```

## Prerequisites

- Python 3.13
- Node.js 22 and npm 10
- A Groq API key
- A Tavily API key
- A Supabase project with Google authentication enabled

The project targets Python 3.13 and Node.js 22. The Python version is recorded
in `.python-version`, while `frontend/package.json` declares the Node version.

## Backend setup

From the repository root:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `backend/.env`, enter your real API keys, and then start the API:

```powershell
uvicorn main:app --reload
```

The API runs at `http://localhost:8000` by default. Check it with
`GET http://localhost:8000/health`. Startup stops with a clear error if a
required environment variable is missing.

## Frontend setup

Open a second terminal and run:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Vite prints the local address, normally `http://localhost:5173`. Keep both
services running while using the application.

`VITE_API_URL` selects the backend used by the frontend. Set it to the local
API during development and to the deployed API URL in the hosting provider.

## Environment variables

### Backend

| Variable | Required | Purpose |
| --- | --- | --- |
| `GROQ_API_KEY` | Yes | Authenticates requests to the Groq-hosted model. |
| `TAVILY_API_KEY` | Yes | Authenticates fallback web searches. |
| `SUPABASE_URL` | Yes | Identifies the Supabase project used for authentication. |
| `SUPABASE_PUBLISHABLE_KEY` | Yes | Lets the backend validate user access tokens with Supabase Auth. |
| `FRONTEND_ORIGINS` | No | Comma-separated browser origins allowed to call the API. |

### Frontend

| Variable | Required | Purpose |
| --- | --- | --- |
| `VITE_API_URL` | No | Base URL for backend API requests; defaults to `http://localhost:8000`. |
| `VITE_SUPABASE_URL` | Yes | Supabase project URL used by the browser. |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | Yes | Public browser key for Supabase Auth. |

Only `VITE_` variables are exposed to browser code. Never put private API keys
in the frontend environment file.

## Current request flow

1. The user signs in with Google through Supabase Auth.
2. The frontend sends the Supabase access token to protected backend endpoints.
3. The backend validates the token with Supabase before creating an in-memory session.
4. A PDF is sent to `POST /upload` and indexed in a session-specific Chroma collection.
5. Questions are sent to `POST /query`.
6. The agent searches document chunks and may fall back to Tavily web search.

## Development checks

```powershell
cd frontend
npm run lint
npm run build
```

## Data, secrets, and current limitations

- Never commit `.env` files, API keys, uploaded PDFs, or user data.
- Local vectors are written to `backend/chroma_db/` and must remain untracked.
- Sessions and conversations are lost when the backend restarts.
- There is no authentication or durable user ownership yet.
- PDF processing occurs synchronously during upload.
- Local Chroma storage is not suitable for multiple deployed API instances.
- Question-bank generation and broader college-document workflows are planned,
  but are not implemented yet.
