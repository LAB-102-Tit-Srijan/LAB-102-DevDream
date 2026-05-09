import os
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException

from app.db.database import supabase_insert

# ── Constants ──────────────────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {".mp4", ".mov"}
UPLOAD_DIR = Path("uploads/videos")

# Folder ensure karo (agar exist na kare)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ── Helper ─────────────────────────────────────────────────────────────────

def _validate_extension(filename: str) -> str:
    """
    File ka extension check karta hai.
    Agar allowed nahi hai toh 400 raise karta hai.
    """
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{ext}'. Only {ALLOWED_EXTENSIONS} allowed."
        )
    return ext


def _generate_unique_filename(ext: str) -> str:
    """
    UUID-based unique filename generate karta hai.
    Example: video_3f4a1bc2.mp4
    Isse original raw filename use nahi hoti → path traversal safe.
    """
    unique_id = uuid.uuid4().hex[:12]
    return f"video_{unique_id}{ext}"


def _save_file_to_disk(file: UploadFile, filename: str) -> Path:
    """
    UploadFile ko disk par safely save karta hai.
    Agar save fail ho toh exception raise karta hai.
    """
    destination = UPLOAD_DIR / filename
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File save failed: {str(e)}"
        )
    finally:
        file.file.close()

    return destination


def _insert_video_metadata(
    title: str,
    subject_name: str,
    file_path: str,
    uploaded_by: str
) -> dict:
    """
    Supabase ke 'videos' table mein video ka record insert karta hai.
    """
    payload = {
        "title": title,
        "subject_name": subject_name or None,
        "file_path": file_path,
        "uploaded_by": uploaded_by or None,
    }
    try:
        record = supabase_insert("videos", payload)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database insert failed: {str(e)}"
        )
    return record


# ── Main Service Function ───────────────────────────────────────────────────

def handle_video_upload(
    file: UploadFile,
    title: str,
    subject_name: str,
    uploaded_by: str
) -> dict:
    """
    Complete video upload workflow:
    1. Validate extension
    2. Generate unique filename
    3. Save file to disk
    4. Insert metadata to DB
    5. Return response data
    """
    # Step 1: Validate
    ext = _validate_extension(file.filename)

    # Step 2: Unique filename
    unique_filename = _generate_unique_filename(ext)

    # Step 3: Save to disk
    saved_path = _save_file_to_disk(file, unique_filename)

    # Step 4: DB insert
    # File path string format: "uploads/videos/video_xyz.mp4"
    relative_path = str(saved_path).replace("\\", "/")
    try:
        record = _insert_video_metadata(title, subject_name, relative_path, uploaded_by)
    except Exception as e:
        # Cleanup orphan file if DB insert fails
        if saved_path.exists():
            saved_path.unlink()
        raise e

    # Step 5: Return clean response data
    return {
        "video_id": record.get("id"),
        "title": record.get("title"),
        "file_path": record.get("file_path"),
    }
