from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from app.schemas.video import VideoUploadResponse
from app.services.video_service import handle_video_upload

# ── Router Setup ───────────────────────────────────────────────────────────
router = APIRouter(
    prefix="/api",
    tags=["Video Upload"],
)


@router.post(
    "/upload-video",
    response_model=VideoUploadResponse,
    summary="Upload a local video file",
    description="""
    Ek local video file (.mp4 ya .mov) upload karo.
    
    - File ko safely `uploads/videos/` mein save kiya jaata hai.
    - Unique UUID-based filename use hota hai (overwrite safe).
    - Metadata PostgreSQL (Supabase) ke `videos` table mein save hota hai.
    - `video_id` return hota hai jo future transcript aur RAG steps mein use hoga.
    """,
)
async def upload_video(
    file: UploadFile = File(..., description="Video file (.mp4 or .mov)"),
    title: str = Form(..., description="Video ka title (required)"),
    subject_name: Optional[str] = Form(None, description="Subject ka naam (optional)"),
    uploaded_by: Optional[str] = Form(None, description="User ka email ya ID (optional)"),
):
    """
    POST /api/upload-video

    Input:
    - file       : .mp4 ya .mov video file
    - title      : Video ka naam
    - subject_name : (optional) Subject
    - uploaded_by  : (optional) User identifier

    Output:
    - video_id, title, file_path
    """
    # Agar file hai hi nahi (empty request)
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    # Core service call
    result_data = handle_video_upload(
        file=file,
        title=title,
        subject_name=subject_name,
        uploaded_by=uploaded_by,
    )

    return VideoUploadResponse(
        status=True,
        message="Video uploaded successfully",
        data=result_data,
    )
