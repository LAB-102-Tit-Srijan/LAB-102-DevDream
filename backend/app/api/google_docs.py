"""
google_docs.py — API routes for Google Docs integration.
Handles OAuth flow, Doc creation, AI notes generation + export.
"""

import os
import logging
from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import RedirectResponse, JSONResponse

from app.services import google_docs_service
from app.services.interaction_service import generate_ai_notes
from app.schemas.interaction import (
    GoogleDocsCreateRequest,
    GoogleDocsAppendRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/google", tags=["Google Docs"])

# ── Auth Dependency (reuse from main.py pattern) ───────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

import requests as http_requests
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


def _verify_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify Supabase JWT and return user dict."""
    token = credentials.credentials
    url = f"{SUPABASE_URL}/auth/v1/user"
    headers = {
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    resp = http_requests.get(url, headers=headers)
    if resp.status_code >= 400:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return resp.json()


# ═══════════════════════════════════════════════════════════════════════════
# 1. OAuth Flow
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/auth/status")
async def google_auth_status(user: dict = Depends(_verify_user)):
    """Check if user has connected Google account."""
    user_id = user["id"]
    connected = google_docs_service.is_connected(user_id)
    
    result = {"status": True, "connected": connected, "auth_url": None}
    
    if not connected:
        try:
            result["auth_url"] = google_docs_service.get_auth_url(user_id)
        except Exception as e:
            logger.warning("Could not generate auth URL: %s", e)
            result["auth_url"] = None
    
    return result


@router.get("/auth/connect")
async def google_auth_connect(user: dict = Depends(_verify_user)):
    """Initiate Google OAuth2 flow — returns auth URL."""
    user_id = user["id"]
    auth_url = google_docs_service.get_auth_url(user_id)
    return {"status": True, "auth_url": auth_url}


@router.get("/callback")
async def google_oauth_callback(code: str = Query(...), state: str = Query("")):
    """
    OAuth2 callback — Google redirects here after user grants permission.
    State contains user_id.
    """
    user_id = state
    if not user_id:
        return JSONResponse(
            status_code=400,
            content={"status": False, "message": "Invalid state parameter"}
        )
    
    google_docs_service.handle_oauth_callback(code, user_id)
    
    # Redirect back to frontend dashboard
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    return RedirectResponse(url=f"{frontend_url}/dashboard?google_connected=true")


# ═══════════════════════════════════════════════════════════════════════════
# 2. Document Operations
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/docs/create")
async def create_google_doc(body: GoogleDocsCreateRequest, user: dict = Depends(_verify_user)):
    """Create a new Google Doc with title and content."""
    user_id = user["id"]
    result = google_docs_service.create_document(user_id, body.title, body.content)
    return {"status": True, "message": "Google Doc created successfully", "data": result}


@router.post("/docs/append")
async def append_to_google_doc(body: GoogleDocsAppendRequest, user: dict = Depends(_verify_user)):
    """Append content to an existing Google Doc."""
    user_id = user["id"]
    result = google_docs_service.append_to_document(user_id, body.doc_id, body.content)
    return {"status": True, "message": "Content appended successfully", "data": result}


# ═══════════════════════════════════════════════════════════════════════════
# 3. AI Notes Generation + Export to Google Docs
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/docs/ai-notes/{video_id}")
async def generate_and_export_notes(video_id: int, user: dict = Depends(_verify_user)):
    """
    Generate AI-powered structured notes from video transcript,
    then optionally export to Google Docs.
    """
    user_id = user["id"]
    
    # Step 1: Generate AI notes
    notes = generate_ai_notes(video_id, user_id)
    
    # Step 2: Try to export to Google Docs (if connected)
    doc_url = None
    if google_docs_service.is_connected(user_id):
        try:
            doc_result = google_docs_service.create_document(
                user_id,
                notes["title"],
                notes["content"]
            )
            doc_url = doc_result["doc_url"]
            logger.info("AI Notes exported to Google Doc: %s", doc_url)
        except Exception as e:
            logger.warning("Google Docs export failed (notes still generated): %s", e)
    
    return {
        "status": True,
        "message": "AI Notes generated successfully" + (" and exported to Google Docs" if doc_url else ""),
        "data": {
            "title": notes["title"],
            "content": notes["content"],
            "video_id": video_id,
            "doc_url": doc_url,
        }
    }


@router.post("/docs/sync-notes/{video_id}")
async def sync_notes_to_docs(video_id: int, user: dict = Depends(_verify_user)):
    """
    Sync all manual notes for a video to a new Google Doc.
    """
    user_id = user["id"]
    
    from app.services.interaction_service import get_notes
    notes = get_notes(video_id, user_id)
    
    if not notes:
        return {"status": False, "message": "No notes to sync."}
    
    # Format notes
    def format_time(seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
    
    formatted = f"StudyAI — Manual Notes\nVideo ID: {video_id}\nGenerated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}\n{'─' * 40}\n\n"
    for note in notes:
        formatted += f"[{format_time(note.get('timestamp', 0))}] — {note.get('content', '')}\n\n"
    
    # Create Google Doc
    doc_result = google_docs_service.create_document(
        user_id,
        f"StudyAI Notes — Video {video_id}",
        formatted
    )
    
    return {
        "status": True,
        "message": "Notes synced to Google Docs",
        "data": doc_result
    }
