import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.db.database import supabase_select
from app.schemas.generate_transcript import (
    GenerateTranscriptErrorResponse,
    GenerateTranscriptRequest,
    GenerateTranscriptResponse,
)
from app.services.auth_service import verify_token
from app.services.generate_transcript_service import (
    DuplicateTranscriptError,
    GenerateTranscriptError,
    TranscriptAlreadyInProgressError,
    TranscriptExecutionError,
    TranscriptMediaValidationError,
    TranscriptStatusUpdateError,
    VideoNotFoundError,
    run_transcript_generation,
)

router = APIRouter(
    prefix="/api",
    tags=["Transcript"],
)

logger = logging.getLogger(__name__)


@router.post(
    "/generate-transcript",
    response_model=GenerateTranscriptResponse,
    summary="Run full transcript generation workflow for a video",
    responses={
        422: {
            "model": GenerateTranscriptErrorResponse,
            "description": "Invalid or unsupported media input",
        },
        404: {
            "model": GenerateTranscriptErrorResponse,
            "description": "video_id does not exist",
        },
        409: {
            "model": GenerateTranscriptErrorResponse,
            "description": "Transcript already exists or is already in progress",
        },
        500: {
            "model": GenerateTranscriptErrorResponse,
            "description": "Internal server error while preparing transcript generation",
        },
    },
)
async def generate_transcript_route(
    payload: GenerateTranscriptRequest,
    user: dict = Depends(verify_token),
):
    logger.info(
        "Generate transcript API request received | video_id=%s | user_id=%s",
        payload.video_id,
        user.get("id"),
    )

    try:
        result = run_transcript_generation(payload.video_id)
    except VideoNotFoundError as exc:
        logger.warning("Validation failure | %s", exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": False,
                "message": exc.message,
                "error": exc.error_detail,
                "data": exc.data.model_dump() if exc.data else None,
            },
        )
    except (DuplicateTranscriptError, TranscriptAlreadyInProgressError) as exc:
        logger.warning("Duplicate generation request | %s", exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": False,
                "message": exc.message,
                "error": exc.error_detail,
                "data": exc.data.model_dump() if exc.data else None,
            },
        )
    except TranscriptStatusUpdateError as exc:
        logger.error("Failed to prepare transcript generation | %s", exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": False,
                "message": exc.message,
                "error": exc.error_detail,
                "data": exc.data.model_dump() if exc.data else None,
            },
        )
    except TranscriptMediaValidationError as exc:
        logger.warning("Transcript media validation failed | %s", exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": False,
                "message": exc.message,
                "error": exc.error_detail,
                "data": exc.data.model_dump() if exc.data else None,
            },
        )
    except TranscriptExecutionError as exc:
        logger.error("Transcript generation execution failed | %s", exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": False,
                "message": exc.message,
                "error": exc.error_detail,
                "data": exc.data.model_dump() if exc.data else None,
            },
        )
    except GenerateTranscriptError as exc:
        logger.error("Generate transcript failed | %s", exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": False,
                "message": exc.message,
                "error": exc.error_detail,
                "data": exc.data.model_dump() if exc.data else None,
            },
        )
    except Exception as exc:
        logger.exception("Unexpected generate transcript failure")
        return JSONResponse(
            status_code=500,
            content={
                "status": False,
                "message": "Transcript generation failed",
                "error": "Unexpected server error while generating transcript.",
                "data": None,
            },
        )

    return GenerateTranscriptResponse(
        status=True,
        message="Transcript generated successfully",
        data=result,
    )

@router.get("/videos/{video_id}/transcript")
async def get_video_transcript(video_id: int, user: dict = Depends(verify_token)):
    """
    Fetch the transcript and video status for a specific video.
    """
    # 1. Check video status first and verify ownership
    videos = supabase_select("videos", {"id": f"eq.{video_id}", "uploaded_by": f"eq.{user['id']}"})
    if not videos:
        raise HTTPException(status_code=404, detail="Video not found or unauthorized")
        
    video = videos[0]
    db_status = video.get("processing_status") or "uploaded"
    
    # 2. Check if transcript ALREADY exists (regardless of video table status)
    # This is a fallback in case the status update in 'videos' table fails (RLS etc.)
    transcripts = supabase_select("transcripts", {"video_id": f"eq.{video_id}"})
    
    if transcripts:
        transcript = transcripts[0]
        return {
            "status": "transcribed",
            "message": "Transcript ready",
            "transcript_data": transcript.get("transcript_json")
        }
        
    # 3. If no transcript yet, return the DB status
    return {
        "status": db_status,
        "message": f"Video is currently {db_status}.",
        "transcript_data": None
    }
