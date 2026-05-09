import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from dotenv import load_dotenv
from models import UserSignup, UserLogin

# Load environment variables
load_dotenv()

app = FastAPI(title="Supabase Auth Backend")

# Setup CORS so the frontend can make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change this to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Initialize Supabase Client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Warning: Supabase credentials not found. Please update the .env file.")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.post("/auth/signup")
async def signup(user: UserSignup):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    try:
        res = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password
        })
        return {"message": "User created successfully.", "data": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login")
async def login(user: UserLogin):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    try:
        res = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })
        return {"message": "Login successful", "session": res.session}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid credentials. Error: {str(e)}")

# Dependency to check JWT token from frontend
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    token = credentials.credentials
    try:
        # get_user automatically verifies the JWT token with Supabase
        res = supabase.auth.get_user(token)
        return res.user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# Example of a protected route
@app.get("/protected")
async def protected_route(user = Depends(verify_token)):
    return {
        "message": "You are authorized!",
        "user_id": user.id,
        "email": user.email
    }

@app.get("/")
async def root():
    return {"message": "Welcome to the Authentication API. Check /docs for Swagger UI."}
