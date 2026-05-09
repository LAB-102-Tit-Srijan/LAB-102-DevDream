import os
import logging
import requests as http_requests
from dotenv import load_dotenv

from pathlib import Path
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_DB_KEY = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY
HTTP_TIMEOUT_SECONDS = int(os.environ.get("SUPABASE_HTTP_TIMEOUT_SECONDS", "30"))

logger = logging.getLogger(__name__)


def get_headers(token: str = None) -> dict:
    """
    Supabase REST API ke liye base headers return karta hai.
    Agar token diya ho toh Authorization header bhi add karta hai.
    """
    if not SUPABASE_DB_KEY:
        raise Exception("Supabase API key is not configured.")

    headers = {
        "apikey": SUPABASE_DB_KEY,
        "Content-Type": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def supabase_insert(table: str, payload: dict) -> dict:
    """
    Kisi bhi table mein ek row insert karta hai aur inserted row return karta hai.
    Production mein yahan service_role key use hogi, par MVP ke liye anon key theek hai.
    """
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = get_headers()
    headers["Prefer"] = "return=representation"  # inserted row wapas bhejo

    response = http_requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=HTTP_TIMEOUT_SECONDS,
    )

    if response.status_code not in (200, 201):
        raise Exception(f"DB insert failed [{response.status_code}]: {response.text}")

    data = response.json()
    if not data:
        raise Exception("DB insert returned empty response.")
    return data[0]


def supabase_select(table: str, filters: dict = None) -> list:
    """
    Kisi table se rows fetch karta hai.
    filters example: {"user_id": "eq.some-uuid"}
    """
    url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
    if filters:
        for key, value in filters.items():
            url += f"&{key}={value}"

    headers = get_headers()
    response = http_requests.get(
        url,
        headers=headers,
        timeout=HTTP_TIMEOUT_SECONDS,
    )

    if response.status_code != 200:
        raise Exception(f"DB select failed [{response.status_code}]: {response.text}")

    return response.json()


def supabase_update(table: str, filters: dict, payload: dict) -> list:
    """
    Kisi table mein rows update karta hai filter ke basis par.
    filters example: {"id": "eq.5"}
    payload example: {"processing_status": "transcribed"}
    Returns list of updated rows.
    """
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if filters:
        params = "&".join(f"{k}={v}" for k, v in filters.items())
        url += f"?{params}"

    headers = get_headers()
    headers["Prefer"] = "return=representation"

    response = http_requests.patch(
        url,
        headers=headers,
        json=payload,
        timeout=HTTP_TIMEOUT_SECONDS,
    )

    logger.debug(
        "PATCH %s | status=%s | payload=%s",
        url,
        response.status_code,
        payload,
    )

    if response.status_code not in (200, 204):
        raise Exception(f"DB update failed [{response.status_code}]: {response.text}")

    if response.status_code == 204:
        return []
    return response.json()
