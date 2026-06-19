"""
app.py — FastAPI application.

Exposes POST /chat and serves the static frontend.
No LLM call anywhere in this file or its imports.
"""

import pathlib
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from safety import check as safety_check
from retrieval import retrieve
from compose import compose

ROOT = pathlib.Path(__file__).parent.parent
FRONTEND_DIR = ROOT / "frontend"

app = FastAPI(title="Sakinah — Islamic Counseling Chatbot")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    sources: list[dict]
    is_crisis: bool
    disclaimer: str


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    crisis = safety_check(req.message)
    if crisis:
        return crisis

    retrieved = retrieve(req.message, top_k=3)
    result = compose(retrieved)
    return result


@app.get("/")
def index():
    return FileResponse(FRONTEND_DIR / "index.html")


# Mount static files last so /chat and / are matched first.
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")
