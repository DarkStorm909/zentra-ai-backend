from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="ZENTRA AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8080",
        "http://localhost:8080",
        "https://zentra-ai-frontend.vercel.app",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "name": "ZENTRA AI",
        "status": "online",
        "version": "0.3",
    }


@app.post("/chat")
def chat(request: ChatRequest):
    message = request.message.strip().lower().rstrip("!.,?")

    if message in ["hello", "hi", "hey"]:
        reply = "Hello, developer! ZENTRA AI is online! ⚡"
    elif "your name" in message:
        reply = "I am ZENTRA AI, your personal chatbot!"
    elif message in ["bye", "goodbye"]:
        reply = "Goodbye, developer!"
    else:
        reply = "I'm still learning. Tell me more!"

    return {"reply": reply}
