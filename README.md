

# 🎥 Video Insight RAG

### **One-line value prop:** Convert video/audio into a searchable transcript and ask natural-language questions — powered by Whisper, embeddings (MiniLM), and a RAG (retrieval-augmented generation) pipeline so you get accurate, transcript-grounded answers.

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](link)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Last Commit](https://img.shields.io/github/last-commit/No0Bitah/Video-Insights-RAG)](link)

[Live Demo](https://youtube.com/shorts/6xBtUXh7CTw?feature=share) • [Documentation](#-documentation--api-reference) • [Report Bug](https://github.com/No0Bitah/Video-Insights-RAG/issues) • [Request Feature](https://github.com/No0Bitah/Video-Insights-RAG/issues)

</div>

---

## 🚀 Overview

**VideoInsight RAG** is a powerful full-stack application that transforms any uploaded audio or video file (like lectures, meetings, or podcasts) into a searchable, conversational knowledge base. It uses FastAPI for a robust backend, Whisper for high-accuracy transcription, Sentence Transformers for efficient vector embeddings, and a flexible architecture that supports both local Ollama models and cloud-based OpenAI for the conversational AI. This allows users to ask questions directly to the content of the media file, bypassing the need to watch the entire recording.

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🗣️ **High-Accuracy Transcription** | Powered by faster-whisper for quick, precise speech-to-text |
| 🧠 **Flexible LLM Support** | Switch between local Ollama models and cloud-based OpenAI |
| 🔍 **RAG-Powered Q&A** | Retrieval Augmented Generation ensures answers grounded in transcript |
| 🌐 **Simple Web Interface** | Drag-and-drop upload with real-time chat capabilities |
| 🚀 **Python Native** | Built with FastAPI for easy extension and deployment |

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [For Hiring Managers](#for-hiring-managers)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Support](#support)


---

## ⚡ Quick Start

### Prerequisites

Before you begin, ensure you have:

- **Python 3.10+**
- **ffmpeg** installed on your system
- **pip** package manager
- Optional: GPU with CUDA for faster transcription
- Optional: **Ollama** running locally (for local LLM mode)
- Optional: **OpenAI API key** (for cloud LLM mode)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/No0Bitah/Video-Insights-RAG.git
   cd Video-Insights-RAG
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate (macOS/Linux)
   source .venv/bin/activate
   
   # Activate (Windows)
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirement.txt
   ```

---

## 🎯 Usage

### Option 1: Run with Ollama (Local)

Ensure Ollama is running on `http://localhost:11434` and you have pulled the model specified in `config.py` (default: `gemma:2b`).

```bash
# Linux/macOS
export LLM_MODE=ollama
uvicorn api:app --reload

# Windows CMD
set LLM_MODE=ollama
uvicorn api:app --reload
```

### Option 2: Run with OpenAI (Cloud)

Set your OpenAI API key as an environment variable.

```bash
# Linux/macOS
export LLM_MODE=openai
export OPENAI_API_KEY="sk-your-api-key-here"
uvicorn api:app --reload

# Windows CMD
set LLM_MODE=openai
set OPENAI_API_KEY=sk-your-api-key-here
uvicorn api:app --reload
```

### Access the Application

Navigate to **`http://127.0.0.1:8000`** in your browser.

---

## 💻 Usage Examples

### Web Interface

1. Start the server
2. Open `http://127.0.0.1:8000/`
3. Upload an audio/video file
4. Click "Transcribe"
5. Start asking questions about the content

### API Usage

**Upload and transcribe:**
```bash
curl -X POST "http://127.0.0.1:8000/transcribe/" \
  -F "file=@/path/to/meeting.mp4"
```

**Ask a question:**
```bash
curl -X POST "http://127.0.0.1:8000/chat/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=What are the next steps?" \
  -d "top_k=3"
```

---

## 📚 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Redirects to the web interface |
| `POST` | `/transcribe/` | Upload audio/video file and receive transcript |
| `POST` | `/chat/` | Ask questions about the transcribed content |

### Core Functions

- **`transcription(file_path)`** - Processes audio/video using Whisper model
- **`load_transcription(text)`** - Splits transcript and creates embeddings
- **`retrieve(query, top_k)`** - Finds relevant chunks via cosine similarity
- **`ask_model(query, top_k)`** - Generates answers using Ollama or OpenAI

---

## 📁 Project Structure

```
video-insight-rag/
├── static/
│   ├── css/
│   │   └── style.css          # Styling for web interface
│   ├── html/
│   │   └── index.html         # Main frontend page
│   └── js/
│       └── script.js          # Frontend logic
├── api.py                     # FastAPI backend (main entry point)
├── config.py                  # Configuration and model settings
└── requirement.txt            # Python dependencies
```

---

## ⚙️ Configuration

Edit `config.py` to customize:

- **Whisper Model**: Change transcription model size
- **Embedding Model**: Modify sentence transformer model
- **LLM Settings**: Configure Ollama model or OpenAI parameters
- **Chunk Settings**: Adjust text splitting parameters

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Install dependencies: `pip install -r requirement.txt`
4. Make your changes and test thoroughly
5. Commit with clear messages: `git commit -m "feat: add new feature"`
6. Push to your fork: `git push origin feat/your-feature`
7. Submit a Pull Request

### Contribution Guidelines

- Follow PEP8 code style
- Keep commits atomic and focused
- Use conventional commit messages (`feat:`, `fix:`, `docs:`, `refactor:`)
- Add tests for new features
- Update documentation as needed

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **No transcript loaded** | Upload a file first using the transcribe endpoint |
| **ffmpeg not found** | Install ffmpeg: `apt-get install ffmpeg` (Linux) or `brew install ffmpeg` (macOS) |
| **OpenAI API error** | Verify `OPENAI_API_KEY` environment variable is set correctly |
| **Ollama connection error** | Ensure Ollama server is running on `http://localhost:11434` |
| **Slow transcription** | Consider using a smaller Whisper model or enabling GPU acceleration |

---

## 🎯 For Hiring Managers

This project demonstrates:

- **Full-stack development** with Python backend and vanilla JS frontend
- **ML/AI integration** using Whisper, embeddings, and RAG architecture
- **API design** with FastAPI and RESTful principles
- **Flexible architecture** supporting multiple LLM providers
- **Production-ready code** with proper structure and documentation

**Tech Stack**: Python • FastAPI • Whisper • Sentence Transformers • Ollama • OpenAI • HTML/CSS/JS

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary

```
Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of the Software.
```

---

## 🙏 Acknowledgements

Built with these amazing technologies:

- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Efficient Whisper implementation
- [sentence-transformers](https://www.sbert.net/) - State-of-the-art sentence embeddings
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [OpenAI](https://openai.com/) - GPT models

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/No0Bitah/Video-Insights-RAG/issues)
- **Discussions**: [GitHub Discussions](https://github.com/No0Bitah/Video-Insights-RAG/discussions)
- **Email**: jomari.daison@gmail.com

---

**Made with ❤️ by [No0Bitah](https://github.com/No0Bitah)**
