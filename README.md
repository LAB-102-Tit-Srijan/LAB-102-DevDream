# StudyAI (LAB-102-DevDream) 🚀

**StudyAI** is an AI-powered Learning Management System (LMS) companion built to revolutionize how students interact with educational video content. This project provides a robust, scalable, and beautifully designed full-stack platform.

## 🌟 Key Features

*   **Secure Authentication:** User signup, login, and protected routes powered by Supabase.
*   **Intelligent Video Uploading:** Secure local storage with metadata synchronization to Supabase PostgreSQL.
*   **⚡ Lightning Fast AI Transcription:** 
    * Utilizes **Groq Cloud Whisper API** (`whisper-large-v3-turbo`) to generate highly accurate, timestamped transcripts from uploaded videos in mere seconds.
    * Includes a robust local offline fallback using `openai-whisper` and `ffmpeg`.
*   **🧠 Context-Aware AI Chatbot & Summary (RAG):**
    * Implements a Retrieval-Augmented Generation (RAG) pipeline using **FAISS** for fast vector search on transcript chunks.
    * Powered by Google's **Gemini (`gemini-flash-latest`)** for intelligent, context-grounded Q&A and video summaries.
    * **Ollama Fallback System:** Automatically routes queries to a locally hosted **Ollama (`llama3.2`)** model to ensure uninterrupted service if the cloud AI API is unavailable or rate-limited.
*   **Live Transcript Viewer:** React frontend component seamlessly polls and displays AI-generated transcripts with elapsed time feedback.
*   **Modern UI/UX:** Responsive, dark-mode focused interface featuring fluid animations and a premium look, built with React and Tailwind CSS.

## 🛠️ Technology Stack

**Frontend:**
*   React.js (Vite)
*   Tailwind CSS
*   Lucide React (Icons)
*   React Router DOM
*   Axios

**Backend:**
*   FastAPI (Python) & Uvicorn
*   Supabase (PostgreSQL Database & Auth via REST API)
*   **AI & ML:** Groq API, Google Generative AI (Gemini), Ollama, FAISS, SentenceTransformers, OpenAI-Whisper
*   **Media Processing:** FFmpeg
*   Pydantic & Python-dotenv

## 🚀 Getting Started

### Prerequisites
*   Node.js & npm
*   Python 3.10+
*   Supabase account and project
*   (Optional) Ollama installed locally for offline AI fallback

### Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Activate the virtual environment:
    ```bash
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure Environment Variables:
    Create a `.env` file in the `backend/` directory:
    ```env
    SUPABASE_URL="your-supabase-url"
    SUPABASE_KEY="your-supabase-anon-key"
    GEMINI_API_KEY="your-gemini-api-key"
    GROQ_API_KEY="your-groq-api-key"
    ```
5.  Start the FastAPI server:
    ```bash
    python -m uvicorn main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`. Documentation can be viewed at `/docs`.

### Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Configure Environment Variables:
    Create a `.env` file in the `frontend/` directory:
    ```env
    VITE_API_URL=http://localhost:8000
    VITE_APP_NAME="StudyAI"
    ```
4.  Start the Vite development server:
    ```bash
    npm run dev
    ```
    The application will be available at `http://localhost:5173`.

## 📂 Project Structure

```text
LAB-102-DevDream/
│
├── backend/                  # FastAPI Backend
│   ├── app/                  # Application logic
│   │   ├── api/              # API Route handlers (Video, Transcript, Chat)
│   │   ├── db/               # Supabase database utilities
│   │   ├── schemas/          # Pydantic models (Data validation)
│   │   └── services/         # Core business logic (AI, RAG, Whisper, Fallbacks)
│   ├── uploads/              # Local storage (videos, embeddings)
│   ├── main.py               # Application entry point
│   └── requirements.txt      # Python dependencies
│
└── frontend/                 # React Frontend
    ├── src/
    │   ├── components/       # Reusable UI (Navbar, ChatInterface, TranscriptViewer)
    │   ├── context/          # React Context (AuthContext)
    │   ├── layouts/          # Page layouts
    │   ├── pages/            # View components
    │   └── services/         # API integration
    └── vite.config.js        # Vite configuration
```

## 📋 Current Development Status

- [x] Backend & Frontend Scaffolded
- [x] Supabase Auth & Profile Management
- [x] Video Upload Workflow
- [x] Speech-to-Text Transcription Integration (Groq + Local Whisper)
- [x] RAG Pipeline for AI Chatbot Querying (FAISS)
- [x] Gemini Integration with Local Ollama Fallback
- [x] End-to-end Integration and Live Sync

---
*Developed for TIT Hackathon 2026*
