# StudyAI (LAB-102-DevDream) 🚀

**StudyAI** is an AI-powered Learning Management System (LMS) companion built to revolutionize how students interact with educational video content. This project provides a robust, scalable, and beautifully designed full-stack platform.

## 🌟 Key Features

*   **Secure Authentication:** User signup, login, and protected routes powered by Supabase.
*   **Profile Management:** Seamless creation and updating of user profiles.
*   **Intelligent Video Uploading:**
    *   Secure local storage (`.mp4`, `.mov`).
    *   UUID-based file naming to prevent overwrites and path traversal vulnerabilities.
    *   Metadata synchronization with Supabase PostgreSQL database.
*   **Modern UI/UX:** Responsive, dark-mode focused interface featuring fluid animations and a premium look, built with React and Tailwind CSS.
*   **AI Chat Interface (Preview):** A dedicated interface designed to query uploaded video content (integration pending).

## 🛠️ Technology Stack

**Frontend:**
*   React.js (Vite)
*   Tailwind CSS
*   Lucide React (Icons)
*   React Router DOM
*   Axios

**Backend:**
*   FastAPI (Python)
*   Uvicorn (ASGI server)
*   Pydantic (Data validation)
*   Supabase (PostgreSQL Database & Auth via REST API)
*   Python-dotenv

## 🚀 Getting Started

### Prerequisites
*   Node.js & npm
*   Python 3.10+
*   Supabase account and project

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
    Ensure you have a `.env` file in the `backend/` directory:
    ```env
    SUPABASE_URL="your-supabase-url"
    SUPABASE_KEY="your-supabase-anon-key"
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
    Create a `.env` file in the `frontend/` directory (optional if backend is on 8000):
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

```
LAB-102-DevDream/
│
├── backend/                  # FastAPI Backend
│   ├── app/                  # Application logic
│   │   ├── api/              # API Route handlers (Video, etc.)
│   │   ├── db/               # Supabase database utilities
│   │   ├── schemas/          # Pydantic models (Data validation)
│   │   └── services/         # Core business logic (Uploads, AI, etc.)
│   ├── uploads/videos/       # Local video storage
│   ├── main.py               # Application entry point & Auth routes
│   ├── models.py             # User models
│   └── requirements.txt      # Python dependencies
│
└── frontend/                 # React Frontend
    ├── src/
    │   ├── components/       # Reusable UI components (Navbar, Loader, ChatInput)
    │   ├── context/          # React Context (AuthContext)
    │   ├── layouts/          # Page layouts (AuthLayout, MainLayout)
    │   ├── pages/            # View components (Home, Login, Signup)
    │   └── services/         # API integration (api.js, authService.js, videoService.js)
    ├── index.css             # Tailwind configuration and global styles
    └── vite.config.js        # Vite bundler configuration
```

## 📋 Current Development Status

- [x] Backend & Frontend Scaffolded
- [x] Supabase Auth Integrated
- [x] Video Upload API & Frontend Component
- [x] Database Schema configured for `videos` and `profiles`
- [ ] Speech-to-Text Transcription Integration
- [ ] RAG Pipeline for AI Chatbot Querying

---
*Developed for TIT Hackathon 2026*
