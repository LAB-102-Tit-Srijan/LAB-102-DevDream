import logging
import os
import shutil
from pathlib import Path
from typing import Any

import ffmpeg

logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parents[2]
VIDEO_UPLOAD_ROOT = (BACKEND_ROOT / "uploads" / "videos").resolve()
LOCAL_RUNTIME_FFMPEG_DIR = (BACKEND_ROOT / ".runtime" / "ffmpeg").resolve()
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov"}
DEFAULT_WHISPER_MODEL = "tiny"


class TranscriptServiceError(Exception):
    """Base exception for controlled transcript generation failures."""


class VideoFileNotFoundError(TranscriptServiceError):
    """Raised when the requested local video file does not exist."""


class UnsafeVideoPathError(TranscriptServiceError):
    """Raised when a video path is outside the allowed uploads/videos folder."""


class UnsupportedVideoFileError(TranscriptServiceError):
    """Raised when the video extension or media probing is not acceptable."""


class FFmpegUnavailableError(TranscriptServiceError):
    """Raised when system FFmpeg is missing or cannot read the media file."""


class WhisperTranscriptionError(TranscriptServiceError):
    """Raised when Whisper cannot load or transcribe the file."""


def generate_transcript(video_file_path: str | Path, model_name: str = DEFAULT_WHISPER_MODEL) -> dict[str, Any]:
    """
    Generate transcript text and timestamped segments for a local uploaded video.

    This function intentionally does not write to the database and does not expose
    an API route. It is the service-only foundation for STEP 2A.
    """
    safe_video_path = _validate_video_path(video_file_path)

    logger.info("Transcription started for video: %s", safe_video_path.name)

    try:
        _verify_ffmpeg_available()
        _probe_video_file(safe_video_path)
        whisper = _import_whisper()
        model = whisper.load_model(model_name)
        result = model.transcribe(str(safe_video_path), fp16=False)
    except TranscriptServiceError as exc:
        logger.warning(
            "Transcription failed for video: %s; reason=%s",
            safe_video_path.name,
            exc,
        )
        raise
    except Exception as exc:
        logger.exception("Transcription failed for video: %s", safe_video_path.name)
        raise WhisperTranscriptionError(f"Whisper transcription failed: {exc}") from exc

    transcript_json = _format_segments(result.get("segments", []))
    transcript_text = (result.get("text") or "").strip()

    logger.info(
        "Transcription success for video: %s; segments=%s",
        safe_video_path.name,
        len(transcript_json),
    )

    return {
        "transcript_text": transcript_text,
        "transcript_json": transcript_json,
    }


def _validate_video_path(video_file_path: str | Path) -> Path:
    if not video_file_path:
        raise VideoFileNotFoundError("Video file path is required.")

    raw_path = Path(video_file_path)
    candidate = raw_path if raw_path.is_absolute() else BACKEND_ROOT / raw_path
    resolved_path = candidate.resolve()

    try:
        resolved_path.relative_to(VIDEO_UPLOAD_ROOT)
    except ValueError as exc:
        raise UnsafeVideoPathError("Video path must be inside uploads/videos/.") from exc

    if not resolved_path.exists() or not resolved_path.is_file():
        raise VideoFileNotFoundError(f"Video file not found: {resolved_path.name}")

    if resolved_path.suffix.lower() not in ALLOWED_VIDEO_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_VIDEO_EXTENSIONS))
        raise UnsupportedVideoFileError(f"Unsupported video type. Allowed extensions: {allowed}.")

    return resolved_path


def _verify_ffmpeg_available() -> None:
    if shutil.which("ffmpeg") is not None:
        return

    try:
        import imageio_ffmpeg

        ffmpeg_exe = Path(imageio_ffmpeg.get_ffmpeg_exe()).resolve()
        if ffmpeg_exe.exists():
            LOCAL_RUNTIME_FFMPEG_DIR.mkdir(parents=True, exist_ok=True)
            local_ffmpeg = LOCAL_RUNTIME_FFMPEG_DIR / "ffmpeg.exe"
            if not local_ffmpeg.exists() or local_ffmpeg.stat().st_size != ffmpeg_exe.stat().st_size:
                shutil.copy2(ffmpeg_exe, local_ffmpeg)

            os.environ["PATH"] = f"{LOCAL_RUNTIME_FFMPEG_DIR}{os.pathsep}{os.environ.get('PATH', '')}"
            if shutil.which("ffmpeg") is not None:
                return
    except Exception:
        logger.debug("imageio-ffmpeg fallback is not available.", exc_info=True)

    if shutil.which("ffmpeg") is None:
        raise FFmpegUnavailableError("System FFmpeg is not installed or not available on PATH.")


def _probe_video_file(video_path: Path) -> None:
    try:
        (
            ffmpeg.input(str(video_path))
            .output("NUL", format="null", t=1, **{"map": "0:a:0"})
            .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        )
    except ffmpeg.Error as exc:
        message = _decode_ffmpeg_error(exc)
        if "matches no streams" in message or "does not contain any stream" in message:
            raise UnsupportedVideoFileError("Video file does not contain an audio stream.") from exc
        raise FFmpegUnavailableError(f"FFmpeg could not read the video file: {message}") from exc


def _import_whisper():
    try:
        import whisper
    except Exception as exc:
        raise WhisperTranscriptionError(
            "openai-whisper is not installed or failed to import."
        ) from exc
    return whisper


def _format_segments(raw_segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    formatted_segments: list[dict[str, Any]] = []

    for segment in raw_segments:
        text = (segment.get("text") or "").strip()
        if not text:
            continue

        formatted_segments.append(
            {
                "text": text,
                "start": round(float(segment.get("start", 0.0)), 2),
                "end": round(float(segment.get("end", 0.0)), 2),
            }
        )

    return formatted_segments


def _decode_ffmpeg_error(exc: ffmpeg.Error) -> str:
    stderr = getattr(exc, "stderr", None)
    if not stderr:
        return str(exc)

    if isinstance(stderr, bytes):
        return stderr.decode("utf-8", errors="replace").strip()

    return str(stderr).strip()
