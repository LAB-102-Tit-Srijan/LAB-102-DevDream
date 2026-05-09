import os
import requests
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from models import UserSignup, UserLogin, UserProfile

# Load environment variables
load_dotenv()

app = FastAPI(title="Supabase Auth Backend (REST API)")

# Setup CORS so the frontend can make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }

@app.post("/auth/signup")
async def signup(user: UserSignup):
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    url = f"{SUPABASE_URL}/auth/v1/signup"
    payload = {"email": user.email, "password": user.password}
    
    response = requests.post(url, headers=get_headers(), json=payload)
    data = response.json()
    
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=data.get("msg") or data.get("error_description") or "Signup failed")
        
    return {"message": "User created successfully.", "data": data}

@app.post("/auth/login")
async def login(user: UserLogin):
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    payload = {"email": user.email, "password": user.password}
    
    response = requests.post(url, headers=get_headers(), json=payload)
    data = response.json()
    
    if response.status_code >= 400:
        raise HTTPException(status_code=401, detail=data.get("error_description", "Invalid credentials"))
        
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

@app.get("/protected")
async def protected_route(user = Depends(verify_token)):
    return {
        "message": "You are authorized!",
        "user": user
    }

@app.get("/profile")
async def get_profile(credentials: HTTPAuthorizationCredentials = Depends(security), user = Depends(verify_token)):
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

@app.post("/profile")
async def update_profile(profile: UserProfile, credentials: HTTPAuthorizationCredentials = Depends(security), user = Depends(verify_token)):
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
        "bio": profile.bio
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=f"Failed to update profile: {response.text}")
        
    return {"message": "Profile updated successfully!"}

@app.get("/")
async def root():
    return {"message": "Welcome to the Authentication API. Check /docs for Swagger UI."}
