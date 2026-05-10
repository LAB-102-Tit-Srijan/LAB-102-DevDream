"""
API routes for Confused Button, AI Quiz, and Smart Notepad.
ADDITIVE router — does not modify any existing routes.
"""

import logging
from fastapi import APIRouter, Depends

from app.schemas.interaction import (
    SimplifyRequest, SimplifyResponse, SimplifyResponseData,
    QuizResponse, QuizResponseData,
    NoteCreate, NoteCreateResponse, NoteOut,
    NotesListResponse,
)
from app.services.auth_service import verify_token
from app.services.interaction_service import (
    simplify_at_timestamp,
    generate_quiz,
    get_notes,
    create_note,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/videos",
    tags=["Interactions"],
)


# ── 1. Confused Button — Simplify ──────────────────────────────────────────

@router.post("/{video_id}/simplify", response_model=SimplifyResponse)
async def simplify_video_moment(
    video_id: int,
    payload: SimplifyRequest,
    user: dict = Depends(verify_token),
):
    """ELI5 explanation of what's happening at the current video timestamp."""
    try:
        result = simplify_at_timestamp(
            video_id=video_id,
            current_time=payload.current_time,
            user_id=user["id"],
        )
        return SimplifyResponse(
            status=True,
            message="Simplified explanation generated",
            data=SimplifyResponseData(**result),
        )
    except Exception as e:
        logger.error("Simplify endpoint error: %s", e, exc_info=True)
        return SimplifyResponse(
            status=False,
            message=str(e),
            data=SimplifyResponseData(
                explanation="Sorry, I couldn't simplify this section right now. Please try again.",
                timestamp_range="N/A",
            ),
        )


# ── 2. AI Quiz ────────────────────────────────────────────────────────────

@router.get("/{video_id}/quiz", response_model=QuizResponse)
async def get_video_quiz(
    video_id: int,
    user: dict = Depends(verify_token),
):
    """Generate 3 MCQ questions based on the video transcript."""
    try:
        questions = generate_quiz(video_id=video_id, user_id=user["id"])
        return QuizResponse(
            status=True,
            message="Quiz generated successfully",
            data=QuizResponseData(questions=questions, video_id=video_id),
        )
    except Exception as e:
        logger.error("Quiz endpoint error: %s", e, exc_info=True)
        return QuizResponse(
            status=False,
            message=str(e),
            data=QuizResponseData(questions=[], video_id=video_id),
        )


# ── 3. Smart Notepad — CRUD ───────────────────────────────────────────────

@router.get("/{video_id}/notes", response_model=NotesListResponse)
async def list_notes(
    video_id: int,
    user: dict = Depends(verify_token),
):
    """Fetch all notes for the current user and video."""
    try:
        notes = get_notes(video_id=video_id, user_id=user["id"])
        return NotesListResponse(
            status=True,
            message="Notes fetched successfully",
            data=[NoteOut(**n) for n in notes],
        )
    except Exception as e:
        logger.error("Notes GET error: %s", e, exc_info=True)
        return NotesListResponse(
            status=False,
            message=str(e),
            data=[],
        )


@router.post("/{video_id}/notes", response_model=NoteCreateResponse)
async def add_note(
    video_id: int,
    payload: NoteCreate,
    user: dict = Depends(verify_token),
):
    """Save a new timestamped note for the current video."""
    try:
        result = create_note(
            video_id=video_id,
            user_id=user["id"],
            content=payload.content,
            timestamp=payload.timestamp,
        )
        return NoteCreateResponse(
            status=True,
            message="Note saved successfully",
            data=NoteOut(**result),
        )
    except Exception as e:
        logger.error("Notes POST error: %s", e, exc_info=True)
        return NoteCreateResponse(
            status=False,
            message=str(e),
            data=NoteOut(
                id=0, user_id="", video_id=video_id,
                content="", timestamp=0.0, created_at=""
            ),
        )
