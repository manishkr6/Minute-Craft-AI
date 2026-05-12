# MinuteCraftAI 🎙️

**MinuteCraftAI** (formerly VoxMind) is a powerful AI-driven video and audio intelligence platform. It allows users to drop in any YouTube link or local video/audio file and automatically transcribes, summarizes, extracts action items, identifies key decisions, and lets you intuitively "chat" with your content using a Retrieval-Augmented Generation (RAG) system.

## 🚀 Key Features

- **Multi-Source Support:** Upload a YouTube URL or drag-and-drop local audio/video files (supports `mp4`, `mp3`, `wav`, `m4a`, `webm`, `ogg`).
- **AI Transcription:** Highly accurate transcriptions using OpenAI's **Whisper** model (with multi-language support including English, Hindi, Hinglish, Spanish, French, and German).
- **Intelligent Summarization:** Generates an executive summary and highlights key points using **Mistral AI** via LangChain.
- **Smart Extraction:** Automatically filters and extracts:
  - ✅ **Action Items** (with task descriptions and deadlines).
  - 🔑 **Key Decisions** made during the video/meeting.
  - ❓ **Open Questions** that remain unresolved.
- **RAG Chat Interface:** Ask questions directly to your video's content! The embedded ChromaDB vector store enables accurate contextual Q&A.
- **Export Reports:** Download comprehensive reports of the analysis in Markdown (`.md`) or text (`.txt`) format.

## 🛠️ Technology Stack

- **Frontend UI:** Streamlit
- **Transcription:** OpenAI Whisper, `yt-dlp`, `pydub`, `ffmpeg`
- **LLM & Orchestration:** Mistral AI, LangChain (`langchain-core`, `langchain-mistralai`)
- **Vector Database (RAG):** ChromaDB
- **Embeddings:** HuggingFace Sentence Transformers

## 📁 Project Structure

```text
minute-craft-ai/
├── app.py                   # Main Streamlit application
├── main.py                  # CLI / Backend runner for the pipeline
├── .env.example             # Template for API keys
├── requirements.txt         # Project dependencies
├── README.md                # Project documentation
├── core/                    # Core AI modules
│   ├── transcriber.py       # Whisper transcription logic
│   ├── summarizer.py        # Mistral-powered text summarization
│   ├── extractor.py         # Extracts action items, decisions, and questions
│   ├── rag_engine.py        # RAG pipeline for the Chat feature
│   └── vector_store.py      # ChromaDB configuration and document loading
└── utils/
    └── audio_processor.py   # Handles YouTube downloading and audio chunking
```

## ⚙️ Installation & Setup

### Prerequisites

1. **Python 3.10+** is recommended.
2. **FFmpeg:** You must have FFmpeg installed on your system for audio extraction to work.
   - **Windows:** Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) or install via `winget install ffmpeg`.
   - **Mac:** `brew install ffmpeg`
   - **Linux:** `sudo apt install ffmpeg`

### 1. Clone the repository

```bash
git clone https://github.com/your-username/minute-craft-ai.git
cd minute-craft-ai
```

### 2. Create a Virtual Environment and Install Dependencies

```bash
python -m venv .venv

# Activate the virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Environment Variables

Rename the `.env.example` file to `.env` and configure your API keys:

```env
# Example .env file
MISTRAL_API_KEY=your_mistral_api_key_here
```

*(Note: Whisper models and HuggingFace embeddings are downloaded and run locally by default, but Mistral AI requires an API key for the summarization and extraction tasks).*

## 💡 Usage

Start the Streamlit Web Application:

```bash
streamlit run app.py
```

### How to use the UI:
1. Open the local address provided by Streamlit (usually `http://localhost:8501`).
2. In the sidebar, select your **Source Type**:
   - Paste a **YouTube URL**.
   - Or **Upload a local file** directly from your machine.
3. Select the spoken language of the video.
4. Click **"⚡ Analyse Now"**. 
5. Wait for the processing pipeline to finish (progress is displayed interactively).
6. Explore the results via the interactive tabs (Summary, Transcript, Action Items, Key Decisions, Open Questions, and Chat).

## 📄 Exporting Results

Once an analysis is complete, you can go to the **📥 Export** tab to download a compiled Markdown or text report containing all extracted knowledge. You can also export the standalone chat logs if you've interacted with the RAG assistant.

---
*Powered by Whisper, Mistral AI, and LangChain.*
