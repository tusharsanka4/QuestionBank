import os
import shutil
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ingest import ingest_pdf
from agent import run_agent

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session history
chat_history = []

class QueryRequest(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    tmp_path = f"/tmp/{file.filename}"
    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    ingest_pdf(tmp_path)
    os.remove(tmp_path)
    
    return {"message": f"{file.filename} uploaded and ingested successfully."}

@app.post("/query")
async def query(request: QueryRequest):
    global chat_history
    response = run_agent(request.question, chat_history)
    chat_history.append({"role": "user", "content": request.question})
    chat_history.append({"role": "assistant", "content": response})
    return {"response": response}

@app.post("/reset")
def reset():
    global chat_history
    chat_history = []
    return {"message": "Session reset."}
