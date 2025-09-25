import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import ollama
import requests
import json
from faster_whisper import WhisperModel


# Ollama API setup
# Define the Ollama API endpoint and the model name
Ollama_API_URL = "http://localhost:11434/api/generate"  # Default endpoint for Ollama
MODEL_NAME = "gemma:2b"  # Replace with your model name if different    

# Initialize Whisper model (tiny/base/small/medium/large-v2)
model = WhisperModel("base", device="cpu", compute_type="int8")

# Initialize MiniLM model for embeddings
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
documents = []
doc_embeddings = None


def transcription(file_path):

    """Transcribe audio file to text using Whisper model.
    Args:
        file_path (str): Path to the audio file.
    Returns:
        str: Full transcript of the audio file.
    """

    # Run transcription (first pass to get info)
    segments, info = model.transcribe(file_path)
    segments = list(segments)  # materialize generator

    # Save full transcript
    for seg in segments:
        full_transcript = " ".join(seg.text.strip() for seg in segments)

    return full_transcript


def load_transcription(txt_file: str):
    """
    Load transcript into vector embeddings using MiniLM.
    """
    global documents, doc_embeddings
    # with open(txt_file, "r", encoding="utf-8") as f:
    #     transcript_text = f.read()

    sentences = txt_file.split(". ")  # split into rough sentences
    documents = [s.strip() for s in sentences if s.strip()]
    doc_embeddings = embedding_model.encode(documents, convert_to_numpy=True)
    print(f"✅ Loaded {len(documents)} chunks into vector store")

def retrieve(query: str, top_k: int = 3):
    """
    Retrieve top_k relevant chunks using cosine similarity.
    """
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    sims = cosine_similarity(query_embedding, doc_embeddings)[0]
    top_indices = np.argsort(sims)[::-1][:top_k]
    return [documents[i] for i in top_indices]

def ask_gemma(query: str, top_k: int = 3):
    """
    Perform RAG: retrieve chunks and send to Gemma3.
    """
    context = retrieve(query, top_k)
    context_text = "\n".join(context)
    headers = {
        "Content-Type": "application/json"
    }

    prompt = f"""You are an assistant using RAG.
            Here is the context from the transcript:

            {context_text}

            Question: {query}
            Answer:"""
    

    # Payload to send to the API (including your prompt)
    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.6,  # Adjust temperature for creativity
        "top_p": 0.9,  # Adjust top_p for diversity
        }
    

    response = requests.post(Ollama_API_URL, headers=headers, data=json.dumps(data))

    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.text}")

    return response.json()["response"]

if __name__ == "__main__":

    # Save full transcript
    txt_file = transcription("1.mp4")

    print("✅ Transcription complete")

    # Load into MiniLM    
    load_transcription(txt_file)


    # Ask Gemma with RAG
    question = "Create a summary of the video"
    answer = ask_gemma(question)
    print("💡 Answer:", answer)