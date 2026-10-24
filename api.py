import os
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from chat import load_responses, reply, MODEL_PATH

BASE_DIR = Path(__file__).resolve().parent
INDEX_PATH = BASE_DIR / "index.html"

app = FastAPI(title="Shop Meal Vietnamese Chatbot", version="1.0.0")

if not os.path.exists(MODEL_PATH):
    raise RuntimeError("Chưa có model. Hãy chạy python train.py trước.")

model = joblib.load(MODEL_PATH)
responses = load_responses()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    reply: str
    intent: str | None
    confidence: float


@app.get("/", include_in_schema=False)
def index():
    # Phục vụ giao diện chat cùng địa chỉ với API nên không cần cấu hình CORS.
    if not INDEX_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy index.html. Hãy đặt file cùng thư mục với api.py.",
        )
    return FileResponse(INDEX_PATH)


@app.get("/health")
def health():
    return {"status": "ok", "service": "shop-meal-chatbot"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer, intent, confidence = reply(model, responses, request.message)
    return ChatResponse(reply=answer, intent=intent, confidence=confidence)