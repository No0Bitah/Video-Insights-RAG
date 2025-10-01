from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import requests
import json
import warnings
import shutil
import os

# OpenAI
from openai import OpenAI

# Local imports
from config import (
    LLM_MODE,
    OLLAMA_API_URL,
    OLLAMA_MODEL_NAME,
    OPENAI_MODEL_NAME,
    OPENAI_API_KEY,
    embedding_model,
    whisper_model,
    system_prompt,
)

warnings.filterwarnings("ignore")

app = FastAPI(title="Speech-to-Text")

# Serve static files (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Allow frontend JS fetch requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

documents = []
doc_embeddings = None
chat_history = []

# Pydantic model for user input
class Question(BaseModel):
    query: str
    top_k: int = 3


# =============================
# FUNCTIONS
# =============================

def transcription(file_path: str) -> str:
    """Transcribe audio file to text using Whisper model."""
    segments, _ = whisper_model.transcribe(file_path)
    segments = list(segments)  # materialize generator

    full_transcript = " ".join(seg.text.strip() for seg in segments)

    with open("transcript.txt", "w", encoding="utf-8") as f:
        f.write(full_transcript)

    return full_transcript


def load_transcription(transcript_text: str):
    """Load transcript into vector embeddings using MiniLM."""
    global documents, doc_embeddings
    sentences = transcript_text.split(". ")
    documents = [s.strip() for s in sentences if s.strip()]
    doc_embeddings = embedding_model.encode(documents, convert_to_numpy=True)


def retrieve(query: str, top_k: int = 3):
    """Retrieve top_k relevant chunks using cosine similarity."""
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    sims = cosine_similarity(query_embedding, doc_embeddings)[0]
    top_indices = np.argsort(sims)[::-1][:top_k]
    return [documents[i] for i in top_indices]


def ask_model(query: str, top_k: int = 3):
    """Perform RAG and query either Ollama or OpenAI."""
    context = retrieve(query, top_k)
    context_text = "\n".join(context)

    prompt = (
        system_prompt
        + context_text
        + "\n\nUser Question: "
        + query
        + "\nAnswer:"
    )

    if LLM_MODE == "ollama":
        # Local Ollama
        data = {
            "model": OLLAMA_MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.6,
            "top_p": 0.9,
        }

        response = requests.post(
            OLLAMA_API_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(data),
        )

        if response.status_code != 200:
            raise Exception(f"Ollama Error: {response.status_code}, {response.text}")

        return response.json()["response"]

    elif LLM_MODE == "openai":
        # OpenAI
        if not OPENAI_API_KEY:
            raise Exception("OpenAI API key not set in environment variables.")

        client = OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{context_text}\n\nQuestion: {query}"},
            ],
            temperature=0.6,
            top_p=0.9,
        )
        return response.choices[0].message.content

    else:
        raise Exception(f"Invalid LLM_MODE: {LLM_MODE}")


# =============================
# API Endpoints
# =============================

@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    """Upload an audio/video file and get transcription."""
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    transcript_text = transcription(temp_file)
    os.remove(temp_file)

    load_transcription(transcript_text)
    return {"transcript": transcript_text}


@app.post("/chat/")
async def chat(query: str = Form(...), top_k: int = Form(3)):
    if not documents:
        return {"error": "No transcript loaded. Upload and transcribe first."}

    history_text = "\n".join(
        [f"User: {h['user']}\nAssistant: {h['assistant']}" for h in chat_history]
    )
    context = retrieve(query, top_k)
    context_text = "\n".join(context)

    # Call model
    answer = ask_model(query, top_k)

    chat_history.append({"user": query, "assistant": answer})

    return {"question": query, "answer": answer, "history": chat_history}


@app.get("/")
async def read_index():
    return RedirectResponse("static/html/index.html")
