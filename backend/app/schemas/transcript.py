"""
Pydantic schemas for transcript data validation.

Used by transcript_storage_service.py to validate data BEFORE it hits
the database.  No API route uses these yet — they exist purely as an
internal contract for service-layer safety.
"""

from typing import Any, List, Optional
from pydantic import BaseModel, Field, field_validator


# ── Segment Schema ──────────────────────────────────────────────────────────
class TranscriptSegment(BaseModel):
    """
    A single timestamped segment inside transcript_json.

    Example:
        {"text": "Today we will learn recursion", "start": 12.4, "end": 18.2}
    """

    text: str = Field(..., min_length=1, description="Segment text content")
    start: float = Field(..., ge=0.0, description="Start time in seconds")
    end: float = Field(..., ge=0.0, description="End time in seconds")

    @field_validator("end")
    @classmethod
    def end_must_be_gte_start(cls, v: float, info) -> float:
        start = info.data.get("start", 0.0)
        if v < start:
            raise ValueError(f"end ({v}) must be >= start ({start})")
        return v


# ── Storage Input Schema ────────────────────────────────────────────────────
class TranscriptSaveInput(BaseModel):
    """
    Input contract for transcript_storage_service.save_transcript().
    Validates everything before a single byte touches the database.
    """

    video_id: int = Field(..., gt=0, description="FK → videos.id")
    transcript_text: str = Field(
        ...,
        min_length=1,
        description="Full transcript as plain text",
    )
    transcript_json: List[TranscriptSegment] = Field(
        ...,
        min_length=1,
        description="List of timestamped segments",
    )


# ── Storage Result Schema ───────────────────────────────────────────────────
class TranscriptSaveResult(BaseModel):
    """Returned by save_transcript() on success."""

    transcript_id: int
    video_id: int
    segments_count: int
    status: str = "success"
