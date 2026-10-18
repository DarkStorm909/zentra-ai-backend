
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

app = FastAPI(title="ZENTRA AI API", version="1.0")

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

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

SYSTEM_INSTRUCTION = """
You are ZENTRA AI, a helpful, intelligent, friendly AI assistant.
Answer clearly and accurately. Explain complex topics step by step.
Help with learning, writing, brainstorming, and programming.
If you are unsure about a fact, be honest rather than inventing details.
Use readable Markdown when useful. Adapt your answer to the user's question.
"""

class ChatMessage(BaseModel):
    role: str
    content: str = Field(min_length=1, max_length=8000)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=12)

@app.get("/")
def home():
    return {
        "name": "ZENTRA AI",
        "status": "online",
        "version": "1.0",
        "engine": "Gemini",
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(request: ChatRequest):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="AI service is not configured yet."
        )

    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    contents = []

    # Accept only valid conversation roles and non-empty messages.
    for item in request.history:
        content = item.content.strip()
        if not content:
            continue

        if item.role == "user":
            role = "user"
        elif item.role in ("assistant", "model"):
            role = "model"
        else:
            continue

        contents.append(
            types.Content(
                role=role,
                parts=[types.Part(text=content)]
            )
        )

    # The latest user message is always appended last.
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part(text=message)]
        )
    )

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=1024,
            ),
        )

        reply = response.text

        if not reply or not reply.strip():
            raise HTTPException(
                status_code=502,
                detail="The AI returned an empty response. Please try again."
            )

        return {"reply": reply.strip()}

    except HTTPException:
        raise
    except Exception:
        # Avoid exposing API keys or internal error details.
        raise HTTPException(
            status_code=502,
            detail="ZENTRA could not get an AI response. Please try again."
        )

