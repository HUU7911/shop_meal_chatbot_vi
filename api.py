import os
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from chat import load_responses, reply, MODEL_PATH

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "chat" / "dist"

app = FastAPI(title="Shop Meal Vietnamese Chatbot", version="1.0.0")

if not os.path.exists(MODEL_PATH):
    raise RuntimeError("Chưa có model. Hãy chạy python train_lr.py trước.")

model = joblib.load(MODEL_PATH)
responses = load_responses()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    reply: str
    intent: str | None
    confidence: float


@app.get("/health")
def health():
    return {"status": "ok", "service": "shop-meal-chatbot"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer, intent, confidence = reply(model, responses, request.message)
    return ChatResponse(reply=answer, intent=intent, confidence=confidence)


if DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="web")
else:
    @app.get("/", include_in_schema=False)
    def index():
        raise HTTPException(
            status_code=404,
            detail="Chưa có giao diện. Vào thư mục shopmeal-chat và chạy: npm install && npm run build",
        )