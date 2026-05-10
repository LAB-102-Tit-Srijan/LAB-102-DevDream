import os
import logging
import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from pathlib import Path

# ── Logging Configuration ───────────────────────────────────────────────────
# Set to INFO so background task logs are visible in console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

from models import UserSignup, UserLogin, UserProfile

# ── New Routers ─────────────────────────────────────────────────────────────
from app.api.video import router as video_router
from app.api.transcript import router as transcript_router
from app.api.chat import router as chat_router
from app.api.interaction import router as interaction_router
from app.api.google_docs import router as google_docs_router

# Load environment variables from the current directory's .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# ── App Init ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="StudyAI Backend",
    description="AI-Powered Learning Companion — FastAPI + Supabase",
    version="1.0.0",
)

# ── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https://.*\.vercel\.app", # Vercel previews allow karega
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static Files (Uploaded Videos) ─────────────────────────────────────────
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ── Include Routers ─────────────────────────────────────────────────────────
app.include_router(video_router)
app.include_router(transcript_router)
app.include_router(chat_router)
app.include_router(interaction_router)
app.include_router(google_docs_router)

# ── Auth Setup ──────────────────────────────────────────────────────────────
security = HTTPBearer()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }


# ── Auth Routes ─────────────────────────────────────────────────────────────

@app.post("/auth/signup", tags=["Authentication"])
async def signup(user: UserSignup):
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Database not configured")

    url = f"{SUPABASE_URL}/auth/v1/signup"
    payload = {"email": user.email, "password": user.password}

    response = requests.post(url, headers=get_headers(), json=payload)
    data = response.json()

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=data.get("msg") or data.get("error_description") or "Signup failed"
        )

    return {"message": "User created successfully.", "data": data}


@app.post("/auth/login", tags=["Authentication"])
async def login(user: UserLogin):
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Database not configured")

    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    payload = {"email": user.email, "password": user.password}

    response = requests.post(url, headers=get_headers(), json=payload)
    data = response.json()

    if response.status_code >= 400:
        raise HTTPException(
            status_code=401,
            detail=data.get("error_description", "Invalid credentials")
        )

    return {"message": "Login successful", "session": data}


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Database not configured")

    token = credentials.credentials
    url = f"{SUPABASE_URL}/auth/v1/user"

    headers = get_headers()
    headers["Authorization"] = f"Bearer {token}"

    response = requests.get(url, headers=headers)
    data = response.json()

    if response.status_code >= 400:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return data


@app.get("/protected", tags=["Authentication"])
async def protected_route(user=Depends(verify_token)):
    return {"message": "You are authorized!", "user": user}


# ── Profile Routes ──────────────────────────────────────────────────────────

@app.get("/profile", tags=["Profile"])
async def get_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user=Depends(verify_token)
):
    token = credentials.credentials
    url = f"{SUPABASE_URL}/rest/v1/profiles?user_id=eq.{user['id']}&select=*"

    headers = get_headers()
    headers["Authorization"] = f"Bearer {token}"

    response = requests.get(url, headers=headers)
    data = response.json()

    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch profile: {data}")

    if not data:
        return {"message": "Profile not found", "profile": None}

    return {"message": "Profile fetched successfully", "profile": data[0]}


@app.post("/profile", tags=["Profile"])
async def update_profile(
    profile: UserProfile,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user=Depends(verify_token)
):
    token = credentials.credentials
    url = f"{SUPABASE_URL}/rest/v1/profiles"

    headers = get_headers()
    headers["Authorization"] = f"Bearer {token}"
    headers["Prefer"] = "resolution=merge-duplicates"

    payload = {
        "user_id": user['id'],
        "name": profile.name,
        "phone": profile.phone,
        "college": profile.college,
        "bio": profile.bio,
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to update profile: {response.text}"
        )

    return {"message": "Profile updated successfully!"}


# ── Root ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "StudyAI Backend is running!",
        "docs": "/docs",
        "version": "1.0.0"
    }


# ── Entry Point ─────────────────────────────────────────────────────────────
# Ab aap `python main.py` se directly server run kar sakte ho!
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Code change hone par auto-restart
    )
