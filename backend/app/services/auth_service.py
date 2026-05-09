import requests
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db.database import SUPABASE_KEY, SUPABASE_URL, get_headers

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Validate bearer token against Supabase Auth and return user payload.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Database not configured")

    token = credentials.credentials
    headers = get_headers(token)

    response = requests.get(f"{SUPABASE_URL}/auth/v1/user", headers=headers, timeout=15)
    data = response.json()

    if response.status_code >= 400:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return data
