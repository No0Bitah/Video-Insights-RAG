from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import requests
import json
import warnings
import shutil
import os

warnings.filterwarnings("ignore")


from config import MODEL_NAME, Ollama_API_URL, embedding_model, model, system_prompt

app = FastAPI(title="Speech-to-Text RAG API")

documents = []
doc_embeddings = None
chat_history = []

# Pydantic model for user input
class Question(BaseModel):
    query: str
    top_k: int = 3

def transcription(file_path: str) -> str:
    """Transcribe audio file to text using Whisper model."""
    segments, info = model.transcribe(file_path)
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


def ask_gemma(query: str, top_k: int = 3):
    """Perform RAG: retrieve chunks and send to Gemma3."""
    context = retrieve(query, top_k)
    context_text = "\n".join(context)

    prompt = (
        system_prompt
        + context_text
        + "\n\nUser Question: "
        + query
        + "\nAnswer:"
    )

    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.6,
        "top_p": 0.9,
    }

    response = requests.post(
        Ollama_API_URL, headers={"Content-Type": "application/json"}, data=json.dumps(data)
    )

    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.text}")

    return response.json()["response"]


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

@app.post("/ask/")
async def ask_question(q: dict):
    if not documents:
        return {"error": "No transcript loaded. Upload and transcribe first."}

    answer = ask_gemma(q["query"], q.get("top_k", 3))
    return {"question": q["query"], "answer": answer}

@app.post("/chat/")
async def chat(q: Question):
    """Conversational Q&A with history."""
    if not documents:
        return {"error": "No transcript loaded. Upload and transcribe first."}

    # Add history to the prompt
    history_text = "\n".join(
        [f"User: {h['user']}\nAssistant: {h['assistant']}" for h in chat_history]
    )

    context = retrieve(q.query, q.top_k)
    context_text = "\n".join(context)

    prompt = (
        system_prompt
        + context_text
        + "\n\nConversation so far:\n"
        + history_text
        + f"\nUser: {q.query}\nAssistant:"
    )

    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.6,
        "top_p": 0.9,
    }

    response = requests.post(
        Ollama_API_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps(data),
    )

    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.text}")

    answer = response.json()["response"]

    # Save to history
    chat_history.append({"user": q.query, "assistant": answer})

    return {"question": q.query, "answer": answer, "history": chat_history}

# Serve index.html when visiting root "/"
@app.get("/")
async def read_index():
    return FileResponse("ui/index.html")


# USAGE
# ``uvicorn api:app --reload``