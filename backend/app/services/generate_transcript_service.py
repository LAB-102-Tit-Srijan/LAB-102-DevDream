import logging
import os
import time
from typing import Any

from pydantic import ValidationError

from app.db.database import supabase_select, supabase_update
from app.schemas.generate_transcript import GenerateTranscriptData
from app.services.transcript_service import (
    DEFAULT_WHISPER_MODEL,
    FFmpegUnavailableError,
    TranscriptServiceError,
    UnsupportedVideoFileError,
    VideoFileNotFoundError,
    WhisperTranscriptionError,
    generate_transcript,
)
from app.services.transcript_storage_service import (
    DuplicateTranscriptError as StorageDuplicateTranscriptError,
    TranscriptInsertError,
    TranscriptStorageError,
    VideoNotFoundError as StorageVideoNotFoundError,
    save_transcript,
)

logger = logging.getLogger(__name__)

STATUS_UPLOADED = "uploaded"
STATUS_TRANSCRIBING = "transcribing"
STATUS_TRANSCRIBED = "transcribed"
STATUS_READY = "ready"
STATUS_FAILED = "failed"

STATUS_UPDATE_RETRIES = int(os.environ.get("TRANSCRIPT_STATUS_UPDATE_RETRIES", "3"))
STATUS_UPDATE_BACKOFF_SECONDS = float(
    os.environ.get("TRANSCRIPT_STATUS_UPDATE_BACKOFF_SECONDS", "0.3")
)


class GenerateTranscriptError(Exception):
    """Base exception for route-safe transcript generation errors."""

    def __init__(
        self,
        error_detail: str,
        *,
        status_code: int = 500,
        message: str = "Transcript generation failed",
        data: GenerateTranscriptData | None = None,
    ):
        super().__init__(error_detail)
        self.error_detail = error_detail
        self.status_code = status_code
        self.message = message
        self.data = data


class VideoNotFoundError(GenerateTranscriptError):
    def __init__(self, error_detail: str):
        super().__init__(error_detail, status_code=404)


class DuplicateTranscriptError(GenerateTranscriptError):
    def __init__(self, error_detail: str, data: GenerateTranscriptData | None = None):
        super().__init__(error_detail, status_code=409, data=data)


class TranscriptAlreadyInProgressError(GenerateTranscriptError):
    def __init__(self, error_detail: str, data: GenerateTranscriptData | None = None):
        super().__init__(error_detail, status_code=409, data=data)


class TranscriptStatusUpdateError(GenerateTranscriptError):
    def __init__(self, error_detail: str, data: GenerateTranscriptData | None = None):
        super().__init__(error_detail, status_code=500, data=data)


class TranscriptMediaValidationError(GenerateTranscriptError):
    def __init__(self, error_detail: str, data: GenerateTranscriptData | None = None):
        super().__init__(error_detail, status_code=422, data=data)


class TranscriptExecutionError(GenerateTranscriptError):
    def __init__(self, error_detail: str, data: GenerateTranscriptData | None = None):
        super().__init__(error_detail, status_code=500, data=data)


def run_transcript_generation(video_id: int) -> dict[str, Any]:
    """
    Full STEP 3B orchestration:
      1) Validate video + duplicate state
      2) Persist status -> transcribing (durable verification)
      3) Run Whisper
      4) Save transcript
      5) Persist status -> transcribed (durable verification)
    """
    logger.info("Generate transcript workflow started | video_id=%s", video_id)

    video = _get_video_or_raise(video_id)
    _ensure_generation_allowed(video_id=video_id, video=video)

    file_path = video.get("file_path")
    if not file_path:
        raise TranscriptExecutionError(
            "Video file path is missing in database record.",
            data=_build_data(video_id, STATUS_FAILED),
        )

    _set_status_verified(video_id, STATUS_TRANSCRIBING)
    logger.info("Status changed | video_id=%s | status=%s", video_id, STATUS_TRANSCRIBING)

    model_name = os.environ.get("WHISPER_MODEL", DEFAULT_WHISPER_MODEL)
    logger.info("Whisper started | video_id=%s | model=%s", video_id, model_name)

    try:
        transcript_payload = generate_transcript(file_path, model_name=model_name)
        logger.info(
            "Whisper success | video_id=%s | segments=%s",
            video_id,
            len(transcript_payload.get("transcript_json", [])),
        )
    except (VideoFileNotFoundError, UnsupportedVideoFileError, FFmpegUnavailableError) as exc:
        _mark_failed_best_effort(video_id)
        raise TranscriptMediaValidationError(
            str(exc),
            data=_build_data(video_id, STATUS_FAILED),
        ) from exc
    except (WhisperTranscriptionError, TranscriptServiceError) as exc:
        _mark_failed_best_effort(video_id)
        raise TranscriptExecutionError(
            str(exc),
            data=_build_data(video_id, STATUS_FAILED),
        ) from exc
    except Exception as exc:
        _mark_failed_best_effort(video_id)
        raise TranscriptExecutionError(
            "Unexpected error during Whisper transcription.",
            data=_build_data(video_id, STATUS_FAILED),
        ) from exc

    try:
        save_result = save_transcript(
            video_id=video_id,
            transcript_text=transcript_payload["transcript_text"],
            transcript_json=transcript_payload["transcript_json"],
            manage_video_status=False,
        )
        logger.info(
            "Transcript save success | video_id=%s | transcript_id=%s",
            video_id,
            save_result.transcript_id,
        )
    except StorageDuplicateTranscriptError as exc:
        # Race-safe handling: if another request inserted it first, block this request as duplicate.
        _set_status_verified(video_id, STATUS_TRANSCRIBED)
        raise DuplicateTranscriptError(
            f"Transcript already exists for video_id={video_id}.",
            data=_build_data(video_id, STATUS_TRANSCRIBED),
        ) from exc
    except (StorageVideoNotFoundError, TranscriptInsertError, TranscriptStorageError, ValidationError) as exc:
        _mark_failed_best_effort(video_id)
        raise TranscriptExecutionError(
            f"Transcript save failed: {exc}",
            data=_build_data(video_id, STATUS_FAILED),
        ) from exc
    except Exception as exc:
        _mark_failed_best_effort(video_id)
        raise TranscriptExecutionError(
            "Unexpected error while saving transcript.",
            data=_build_data(video_id, STATUS_FAILED),
        ) from exc

    _set_status_verified(video_id, STATUS_TRANSCRIBED)
    logger.info("Final status update success | video_id=%s | status=%s", video_id, STATUS_TRANSCRIBED)

    return _build_data(video_id, STATUS_TRANSCRIBED).model_dump()


def _get_video_or_raise(video_id: int) -> dict[str, Any]:
    rows = supabase_select("videos", {"id": f"eq.{video_id}"})
    if not rows:
        raise VideoNotFoundError(f"Video with id={video_id} does not exist.")
    return rows[0]


def _ensure_generation_allowed(video_id: int, video: dict[str, Any]) -> None:
    current_status = str(video.get("processing_status") or STATUS_UPLOADED).lower()

    if current_status == STATUS_TRANSCRIBING:
        raise TranscriptAlreadyInProgressError(
            f"Transcript generation is already in progress for video_id={video_id}.",
            data=_build_data(video_id, STATUS_TRANSCRIBING),
        )

    existing_transcripts = supabase_select("transcripts", {"video_id": f"eq.{video_id}"})
    if existing_transcripts:
        raise DuplicateTranscriptError(
            f"Transcript already exists for video_id={video_id}.",
            data=_build_data(video_id, STATUS_TRANSCRIBED),
        )


def _set_status_verified(video_id: int, target_status: str) -> None:
    last_reason: str | None = None

    for attempt in range(1, STATUS_UPDATE_RETRIES + 1):
        try:
            supabase_update(
                "videos",
                {"id": f"eq.{video_id}"},
                {"processing_status": target_status},
            )

            latest = _get_video_or_raise(video_id)
            persisted_status = str(
                latest.get("processing_status") or STATUS_UPLOADED
            ).lower()

            if persisted_status == target_status:
                return

            last_reason = (
                f"status mismatch after update (expected={target_status}, actual={persisted_status})"
            )
            logger.warning(
                "Status verify mismatch | video_id=%s | attempt=%s/%s | %s",
                video_id,
                attempt,
                STATUS_UPDATE_RETRIES,
                last_reason,
            )
        except Exception as exc:
            last_reason = str(exc)
            logger.warning(
                "Status update attempt failed | video_id=%s | target_status=%s | "
                "attempt=%s/%s | error=%s",
                video_id,
                target_status,
                attempt,
                STATUS_UPDATE_RETRIES,
                exc,
            )

        if attempt < STATUS_UPDATE_RETRIES:
            time.sleep(STATUS_UPDATE_BACKOFF_SECONDS * attempt)

    raise TranscriptStatusUpdateError(
        (
            f"Could not persist processing_status='{target_status}' for video_id={video_id}. "
            f"Possible Supabase policy restriction. Last reason: {last_reason or 'unknown'}"
        ),
        data=_build_data(video_id, STATUS_FAILED if target_status != STATUS_TRANSCRIBED else STATUS_TRANSCRIBED),
    )


def _mark_failed_best_effort(video_id: int) -> None:
    try:
        _set_status_verified(video_id, STATUS_FAILED)
        logger.info("Status changed | video_id=%s | status=%s", video_id, STATUS_FAILED)
    except GenerateTranscriptError as exc:
        logger.error(
            "Failed to mark video as failed | video_id=%s | reason=%s",
            video_id,
            exc.error_detail,
        )
    except Exception as exc:
        logger.error(
            "Failed to mark video as failed | video_id=%s | reason=%s",
            video_id,
            exc,
        )


def _build_data(video_id: int, status: str) -> GenerateTranscriptData:
    return GenerateTranscriptData(video_id=video_id, processing_status=status)
