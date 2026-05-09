import os
import requests as http_requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


def get_headers(token: str = None) -> dict:
    """
    Supabase REST API ke liye base headers return karta hai.
    Agar token diya ho toh Authorization header bhi add karta hai.
    """
    headers = {
        "apikey": SUPABASE_KEY,
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

    response = http_requests.post(url, headers=headers, json=payload)

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
    response = http_requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"DB select failed [{response.status_code}]: {response.text}")

    return response.json()
