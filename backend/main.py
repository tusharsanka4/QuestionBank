import os
import shutil
import uuid
import tempfile
from config import settings
from fastapi import Depends, FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from ingest import ingest_pdf
from agent import run_agent
from auth import AuthenticatedUser, get_current_user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.frontend_origins),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Per-session storage
# { session_id: [{"role": ..., "content": ...}, ...] }
session_histories: dict[str, list] = {}

class QueryRequest(BaseModel):
    question: str

def get_or_create_history(session_id: str) -> list:
    if session_id not in session_histories:
        session_histories[session_id] = []
    return session_histories[session_id]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/session")
def create_session(_user: AuthenticatedUser = Depends(get_current_user)):
    """Frontend calls this on load to get a unique session ID."""
    session_id = str(uuid.uuid4())
    session_histories[session_id] = []
    return {"session_id": session_id}

@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    x_session_id: Optional[str] = Header(None),
    _user: AuthenticatedUser = Depends(get_current_user),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    if not x_session_id:
        raise HTTPException(status_code=400, detail="Missing session ID.")

    tmp_path = os.path.join(tempfile.gettempdir(), f"{x_session_id}_{file.filename}")
    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    ingest_pdf(tmp_path, session_id=x_session_id)
    os.remove(tmp_path)

    return {"message": f"{file.filename} uploaded and ingested successfully."}

@app.post("/query")
async def query(
    request: QueryRequest,
    x_session_id: Optional[str] = Header(None),
    _user: AuthenticatedUser = Depends(get_current_user),
):
    if not x_session_id:
        raise HTTPException(status_code=400, detail="Missing session ID.")

    history = get_or_create_history(x_session_id)
    response = run_agent(request.question, history, session_id=x_session_id)
    history.append({"role": "user", "content": request.question})
    history.append({"role": "assistant", "content": response})
    return {"response": response}

@app.post("/reset")
def reset(
    x_session_id: Optional[str] = Header(None),
    _user: AuthenticatedUser = Depends(get_current_user),
):
    if x_session_id and x_session_id in session_histories:
        session_histories[x_session_id] = []
    return {"message": "Session reset."}
