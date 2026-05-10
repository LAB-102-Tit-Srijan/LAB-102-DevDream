"""
google_docs_service.py — Google Docs integration for StudyAI.
Handles OAuth2 token management, Doc creation, and content appending.
ADDITIVE file — does not modify any existing service.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# ── OAuth2 Config ───────────────────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]

# Paths for credentials
CREDENTIALS_DIR = Path("credentials")
CREDENTIALS_DIR.mkdir(exist_ok=True)

CLIENT_SECRETS_FILE = os.environ.get(
    "GOOGLE_CLIENT_SECRETS_FILE",
    str(CREDENTIALS_DIR / "client_secret.json")
)

REDIRECT_URI = os.environ.get(
    "GOOGLE_OAUTH_REDIRECT_URI",
    "http://localhost:8000/api/google/callback"
)


def _get_token_path(user_id: str) -> Path:
    """Get user-specific token storage path."""
    return CREDENTIALS_DIR / f"token_{user_id}.json"


def _load_credentials(user_id: str) -> Optional[Credentials]:
    """Load stored OAuth2 credentials for a user."""
    token_path = _get_token_path(user_id)
    if not token_path.exists():
        return None
    
    try:
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        # Auto-refresh if expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            _save_credentials(user_id, creds)
        return creds if creds and creds.valid else None
    except Exception as e:
        logger.error("Failed to load Google credentials for %s: %s", user_id, e)
        return None


def _save_credentials(user_id: str, creds: Credentials):
    """Save OAuth2 credentials to disk."""
    token_path = _get_token_path(user_id)
    token_path.write_text(creds.to_json())


def get_auth_url(user_id: str) -> str:
    """Generate Google OAuth2 authorization URL."""
    if not Path(CLIENT_SECRETS_FILE).exists():
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured. Place client_secret.json in /credentials/"
        )
    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=user_id,  # Pass user_id as state for callback
    )
    
    return auth_url


def handle_oauth_callback(code: str, user_id: str) -> bool:
    """Exchange authorization code for tokens and save."""
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
        )
        flow.fetch_token(code=code)
        creds = flow.credentials
        _save_credentials(user_id, creds)
        logger.info("Google OAuth tokens saved for user %s", user_id)
        return True
    except Exception as e:
        logger.error("OAuth callback failed: %s", e)
        raise HTTPException(status_code=500, detail=f"OAuth failed: {str(e)}")


def is_connected(user_id: str) -> bool:
    """Check if user has valid Google credentials."""
    creds = _load_credentials(user_id)
    return creds is not None and creds.valid


def _get_docs_service(user_id: str):
    """Build Google Docs API service."""
    creds = _load_credentials(user_id)
    if not creds:
        raise HTTPException(
            status_code=401,
            detail="Google account not connected. Please authorize first."
        )
    return build("docs", "v1", credentials=creds)


def _get_drive_service(user_id: str):
    """Build Google Drive API service."""
    creds = _load_credentials(user_id)
    if not creds:
        raise HTTPException(
            status_code=401,
            detail="Google account not connected. Please authorize first."
        )
    return build("drive", "v3", credentials=creds)


# ═══════════════════════════════════════════════════════════════════════════
# DOCUMENT OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════

def create_document(user_id: str, title: str, content: str) -> dict:
    """
    Create a new Google Doc with title and content.
    Returns: { doc_id, doc_url, title }
    """
    docs_service = _get_docs_service(user_id)
    
    # Step 1: Create empty document
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]
    
    # Step 2: Insert content
    if content.strip():
        requests_body = [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": content
                }
            }
        ]
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": requests_body}
        ).execute()
    
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    
    logger.info("Created Google Doc '%s' for user %s: %s", title, user_id, doc_url)
    
    return {
        "doc_id": doc_id,
        "doc_url": doc_url,
        "title": title,
    }


def append_to_document(user_id: str, doc_id: str, content: str) -> dict:
    """Append content to an existing Google Doc."""
    docs_service = _get_docs_service(user_id)
    
    # Get current document length
    doc = docs_service.documents().get(documentId=doc_id).execute()
    end_index = doc["body"]["content"][-1]["endIndex"] - 1
    
    # Insert at the end
    requests_body = [
        {
            "insertText": {
                "location": {"index": end_index},
                "text": f"\n\n{content}"
            }
        }
    ]
    
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": requests_body}
    ).execute()
    
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    
    return {
        "doc_id": doc_id,
        "doc_url": doc_url,
        "appended": True,
    }
