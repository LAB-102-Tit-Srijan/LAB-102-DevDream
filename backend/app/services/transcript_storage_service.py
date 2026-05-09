"""
STEP 2B — Transcript Storage Service
=====================================

Responsibility:
    Take the transcript output from STEP 2A (transcript_text + transcript_json)
    and persist it into the PostgreSQL `transcripts` table via Supabase REST API.

This module does NOT:
    - Expose any API route
    - Generate transcripts (that is STEP 2A)
    - Create embeddings or vectors (that is STEP 3)

Architecture:
    save_transcript()
        ├── validate input via Pydantic schemas
        ├── verify video_id exists in `videos` table
        ├── check for duplicate transcript
        ├── update video processing_status → "transcribing"
        ├── insert transcript row into `transcripts` table
        ├── update video processing_status → "transcribed"
        └── return TranscriptSaveResult
"""

import json
import logging
from typing import Any

from app.db.database import supabase_insert, supabase_select, supabase_update
from app.schemas.transcript import (
    TranscriptSaveInput,
    TranscriptSaveResult,
    TranscriptSegment,
)

logger = logging.getLogger(__name__)


# ── Custom Exceptions ───────────────────────────────────────────────────────

class TranscriptStorageError(Exception):
    """Base exception for transcript storage failures."""


class VideoNotFoundError(TranscriptStorageError):
    """Raised when video_id does not exist in the videos table."""


class DuplicateTranscriptError(TranscriptStorageError):
    """Raised when a transcript already exists for the given video_id."""


class TranscriptInsertError(TranscriptStorageError):
    """Raised when the database INSERT for the transcript fails."""


class VideoStatusUpdateError(TranscriptStorageError):
    """Raised when updating video processing_status fails."""


# ── Main Public Function ───────────────────────────────────────────────────

def save_transcript(
    video_id: int,
    transcript_text: str,
    transcript_json: list[dict[str, Any]],
    manage_video_status: bool = True,
) -> TranscriptSaveResult:
    """
    Validate and persist a generated transcript to PostgreSQL.

    Args:
        video_id:         FK → videos.id (must exist)
        transcript_text:  Full plaintext transcript from Whisper
        transcript_json:  List of timestamped segments from Whisper

    Returns:
        TranscriptSaveResult on success

    Raises:
        VideoNotFoundError        — video_id not in videos table
        DuplicateTranscriptError  — transcript already exists for this video
        TranscriptInsertError     — DB insert failed
        ValidationError           — Pydantic rejected the input data
    """
    logger.info("Transcript save started | video_id=%s", video_id)

    # ── Step 1: Validate input data via Pydantic ────────────────────────
    validated_segments = [TranscriptSegment(**seg) for seg in transcript_json]
    validated_input = TranscriptSaveInput(
        video_id=video_id,
        transcript_text=transcript_text,
        transcript_json=validated_segments,
    )

    logger.info(
        "Input validation passed | video_id=%s | segments=%s",
        validated_input.video_id,
        len(validated_input.transcript_json),
    )

    # ── Step 2: Verify video_id exists ──────────────────────────────────
    _verify_video_exists(validated_input.video_id)

    # ── Step 3: Check for duplicate transcript ──────────────────────────
    _check_duplicate_transcript(validated_input.video_id)

    # ── Step 4: Update processing_status → "transcribing" ──────────────
    if manage_video_status:
        _update_video_status(validated_input.video_id, "transcribing")

    # ── Step 5: Insert transcript into database ─────────────────────────
    try:
        payload = {
            "video_id": validated_input.video_id,
            "transcript_text": validated_input.transcript_text,
            "transcript_json": json.loads(
                json.dumps(
                    [seg.model_dump() for seg in validated_input.transcript_json]
                )
            ),
        }

        record = supabase_insert("transcripts", payload)

        transcript_id = record.get("id")
        if not transcript_id:
            raise TranscriptInsertError("DB returned record without 'id' field.")

        logger.info(
            "Transcript inserted successfully | transcript_id=%s | video_id=%s",
            transcript_id,
            validated_input.video_id,
        )

    except TranscriptInsertError:
        # Our own error, rollback status and re-raise
        if manage_video_status:
            _update_video_status(validated_input.video_id, "failed")
        raise
    except Exception as exc:
        # Unexpected DB failure, rollback status
        if manage_video_status:
            _update_video_status(validated_input.video_id, "failed")
        logger.error(
            "Transcript insert FAILED | video_id=%s | error=%s",
            validated_input.video_id,
            exc,
        )
        raise TranscriptInsertError(f"Database insert failed: {exc}") from exc

    # ── Step 6: Update processing_status → "transcribed" ────────────────
    if manage_video_status:
        _update_video_status(validated_input.video_id, "transcribed")

    result = TranscriptSaveResult(
        transcript_id=transcript_id,
        video_id=validated_input.video_id,
        segments_count=len(validated_input.transcript_json),
        status="success",
    )

    logger.info(
        "Transcript save SUCCESS | transcript_id=%s | video_id=%s | segments=%s",
        result.transcript_id,
        result.video_id,
        result.segments_count,
    )

    return result


# ── Internal Helpers ────────────────────────────────────────────────────────

def _verify_video_exists(video_id: int) -> None:
    """Check that the video_id actually exists in the videos table."""
    try:
        rows = supabase_select("videos", {"id": f"eq.{video_id}"})
    except Exception as exc:
        raise VideoNotFoundError(
            f"Could not verify video_id={video_id}: {exc}"
        ) from exc

    if not rows:
        raise VideoNotFoundError(f"No video found with id={video_id}")

    logger.info("Video exists check passed | video_id=%s", video_id)


def _check_duplicate_transcript(video_id: int) -> None:
    """Reject if a transcript row already exists for this video."""
    try:
        rows = supabase_select("transcripts", {"video_id": f"eq.{video_id}"})
    except Exception as exc:
        # If the table doesn't exist yet, supabase will return an error.
        # We treat that as "no duplicates" and let the insert fail later
        # with a more descriptive error.
        logger.warning(
            "Duplicate check query failed (table may not exist yet): %s", exc
        )
        return

    if rows:
        raise DuplicateTranscriptError(
            f"Transcript already exists for video_id={video_id} "
            f"(transcript_id={rows[0].get('id')})"
        )

    logger.info("Duplicate check passed | video_id=%s", video_id)


def _update_video_status(video_id: int, status: str) -> None:
    """
    Update the processing_status column in the videos table.
    Fails silently with a warning if the column doesn't exist yet
    (graceful degradation for hackathon safety).
    """
    try:
        supabase_update(
            "videos",
            {"id": f"eq.{video_id}"},
            {"processing_status": status},
        )
        logger.info(
            "Video status updated | video_id=%s | status=%s", video_id, status
        )
    except Exception as exc:
        # If processing_status column doesn't exist, log warning but don't crash
        logger.warning(
            "Could not update video processing_status | video_id=%s | error=%s",
            video_id,
            exc,
        )
