from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ProcessingStatus = Literal["uploaded", "transcribing", "transcribed", "ready", "failed"]


class GenerateTranscriptRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"example": {"video_id": 1}},
    )

    video_id: int = Field(
        ...,
        strict=True,
        gt=0,
        description="Existing video ID (strict positive integer)",
    )


class GenerateTranscriptData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    video_id: int = Field(..., gt=0, description="Video ID for generation request")
    processing_status: ProcessingStatus = Field(
        ...,
        description="Current processing state for the video",
    )


class GenerateTranscriptResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: bool = True
    message: str
    data: GenerateTranscriptData


class GenerateTranscriptErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: bool = False
    message: str
    error: str
    data: GenerateTranscriptData | None = None
