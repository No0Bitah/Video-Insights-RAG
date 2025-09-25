from faster_whisper import WhisperModel
from sentence_transformers import SentenceTransformer


# Ollama API setup
# Define the Ollama API endpoint and the model name
Ollama_API_URL = "http://localhost:11434/api/generate"  # Default endpoint for Ollama
MODEL_NAME = "gemma:2b"  # Replace with your model name if different    

# Initialize Whisper model (tiny/base/small/medium/large-v2)
model = WhisperModel("base", device="cpu", compute_type="int8")

# Initialize MiniLM model for embeddings
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')



system_prompt = f"""
You are an AI assistant that analyzes video transcripts. 
The transcript represents the full content of the video. 

RULE!
You will answer the query using the process:
1. Analayze thoughroly the transcripts context



Transcript Context:

"""

