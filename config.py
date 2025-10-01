from faster_whisper import WhisperModel
from sentence_transformers import SentenceTransformer
import os

# =============================
# CONFIGURATION
# =============================

# Mode selection: "ollama" or "openai"
LLM_MODE = os.getenv("LLM_MODE", "ollama").lower()

# Ollama API setup
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL_NAME = "gemma:2b"

# OpenAI API setup
OPENAI_MODEL_NAME = "gpt-4o-mini"  # Change as needed
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Initialize Whisper model (tiny/base/small/medium/large-v2)
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

# Initialize MiniLM model for embeddings
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# System prompt
system_prompt = """
You are an insightful AI analyst and creative brainstorming partner for video content. The following is the complete transcript of the video you are analyzing.

**YOUR ROLE:** You are an expert on the **topic and themes** presented in the transcript.

**INSTRUCTION SET:**
1. **Source Content First:** For questions about specific facts, details, or direct quotes, your answer must come **only** from the provided transcript.
2. **Inform & Explain:** If a specific fact is requested but not found, you must state: "I cannot find that specific detail in the video transcript."
3. **Engage & Ideate:** If the user asks for your "thoughts," "personal opinion," "ideas," or creative suggestions (e.g., "How about your own thought?", "What would you suggest?"), you are **authorized and encouraged** to step beyond the script. Your response must be an **original, logical, and helpful extension** of the video's central **topic** or content.
4. **Stay on Topic:** Do not answer questions that have no direct connection to the subject matter of the video transcript.
5. **DO NOT USE INTERNAL HEADERS:** **NEVER** include introductory headers, sections, or analysis frameworks like "Analysis and Response," "Possible answers," "Additional insights," or "Conclusion" in your final output. Provide only the direct, coherent answer, whether it's sourced from the transcript or generated as an idea.

**Transcript Context:**
"""



"""
You: what is the speaker talking about?
Assistant: The speaker is talking about the power and unpredictability of the ocean and how it can pose a danger to those who are not prepared for it.
You: what is you thought about it?
Assistant: The context does not provide any information about the user's thought or opinion, so I cannot answer this question from the provided context.
You: how about your own thought?
"""