from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from typing import Optional

from app.schemas.video import VideoUploadResponse
from app.services.video_service import handle_video_upload
from app.services.tasks import process_video_transcript_background
from app.services.auth_service import verify_token

# ── Router Setup ───────────────────────────────────────────────────────────
router = APIRouter(
    prefix="/api",
    tags=["Video Upload"],
)


@router.post(
    "/upload-video",
    response_model=VideoUploadResponse,
    summary="Upload a local video file",
)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Video file (.mp4 or .mov)"),
    title: str = Form(..., description="Video ka title (required)"),
    subject_name: Optional[str] = Form(None, description="Subject ka naam (optional)"),
    user: dict = Depends(verify_token)
):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    # 200MB size limit check
    MAX_SIZE = 200 * 1024 * 1024
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 200MB.")

    # Core service call
    result_data = handle_video_upload(
        file=file,
        title=title,
        subject_name=subject_name,
        uploaded_by=user["id"],
    )
    
    # Trigger background transcription
    background_tasks.add_task(
        process_video_transcript_background, 
        video_id=result_data["video_id"], 
        file_path=result_data["file_path"]
    )

    return VideoUploadResponse(
        status=True,
        message="Video uploaded successfully. Transcription started in background.",
        data=result_data,
    )
