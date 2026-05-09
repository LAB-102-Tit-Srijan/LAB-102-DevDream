import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

import ffmpeg
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

BACKEND_ROOT = Path(__file__).resolve().parents[2]
VIDEO_UPLOAD_ROOT = (BACKEND_ROOT / "uploads" / "videos").resolve()
LOCAL_RUNTIME_FFMPEG_DIR = (BACKEND_ROOT / ".runtime" / "ffmpeg").resolve()
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov"}
DEFAULT_WHISPER_MODEL = "tiny"

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")


# ── Exceptions ──────────────────────────────────────────────────────────────

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


# ── Main Public Function ───────────────────────────────────────────────────

def generate_transcript(
    video_file_path: str | Path,
    model_name: str = DEFAULT_WHISPER_MODEL,
) -> dict[str, Any]:
    """
    Generate transcript text and timestamped segments for a local uploaded video.
    
    Strategy:
      1. Try Groq Cloud Whisper API first (3-5 seconds, high accuracy)
      2. Fall back to local Whisper if Groq fails or key is missing
    """
    safe_video_path = _validate_video_path(video_file_path)

    # ── Strategy 1: Groq Cloud Whisper (FAST) ───────────────────────────
    if GROQ_API_KEY:
        logger.info("Groq API key found — using cloud transcription | file=%s", safe_video_path.name)
        try:
            return _transcribe_with_groq(safe_video_path)
        except Exception as exc:
            logger.warning(
                "Groq transcription failed, falling back to local Whisper | error=%s", exc
            )
    else:
        logger.info("No GROQ_API_KEY — using local Whisper | file=%s", safe_video_path.name)

    # ── Strategy 2: Local Whisper (SLOW fallback) ───────────────────────
    return _transcribe_with_local_whisper(safe_video_path, model_name)


# ── Groq Cloud Transcription ───────────────────────────────────────────────

def _transcribe_with_groq(video_path: Path) -> dict[str, Any]:
    """
    Use Groq's Whisper large-v3-turbo for ultra-fast cloud transcription.
    Extracts audio first to reduce upload payload.
    """
    from groq import Groq

    logger.info("Groq transcription started | file=%s", video_path.name)

    # Extract audio to temp file for smaller upload
    audio_path = _extract_audio(video_path)

    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        with open(audio_path, "rb") as audio_file:
            result = client.audio.transcriptions.create(
                file=(audio_path.name, audio_file),
                model="whisper-large-v3-turbo",
                response_format="verbose_json",
                timestamp_granularities=["segment"],
                language="en",
            )

        # Parse Groq response
        transcript_text = (result.text or "").strip()
        if not transcript_text:
            raise WhisperTranscriptionError("Groq returned empty transcript text.")

        segments = getattr(result, "segments", []) or []
        transcript_json = _format_groq_segments(segments)

        logger.info(
            "Groq transcription SUCCESS | file=%s | segments=%s",
            video_path.name,
            len(transcript_json),
        )

        return {
            "transcript_text": transcript_text,
            "transcript_json": transcript_json,
        }

    finally:
        # Clean up temp audio file
        if audio_path and audio_path.exists() and audio_path != video_path:
            try:
                audio_path.unlink()
            except Exception:
                pass


def _extract_audio(video_path: Path) -> Path:
    """Extract audio from video to a temporary WAV file for API upload."""
    _verify_ffmpeg_available()

    temp_dir = tempfile.mkdtemp()
    audio_path = Path(temp_dir) / f"{video_path.stem}_audio.mp3"

    try:
        (
            ffmpeg.input(str(video_path))
            .output(str(audio_path), acodec="libmp3lame", ac=1, ar="16000", audio_bitrate="64k")
            .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        )
    except ffmpeg.Error as exc:
        message = _decode_ffmpeg_error(exc)
        raise FFmpegUnavailableError(f"Audio extraction failed: {message}") from exc

    if not audio_path.exists() or audio_path.stat().st_size == 0:
        raise FFmpegUnavailableError("Audio extraction produced empty file.")

    logger.info("Audio extracted | size=%s KB", audio_path.stat().st_size // 1024)
    return audio_path


def _format_groq_segments(segments: list) -> list[dict[str, Any]]:
    """Format Groq API segments into our standard format."""
    formatted = []
    for seg in segments:
        text = ""
        start_sec = 0.0
        end_sec = 0.0

        if isinstance(seg, dict):
            text = (seg.get("text") or "").strip()
            start_sec = round(float(seg.get("start", 0.0)), 2)
            end_sec = round(float(seg.get("end", 0.0)), 2)
        else:
            # Groq Pydantic model object
            text = (getattr(seg, "text", "") or "").strip()
            start_sec = round(float(getattr(seg, "start", 0.0)), 2)
            end_sec = round(float(getattr(seg, "end", 0.0)), 2)

        if not text:
            continue

        minutes = int(start_sec // 60)
        seconds = int(start_sec % 60)
        time_str = f"{minutes}:{seconds:02d}"

        formatted.append({
            "text": text,
            "start": start_sec,
            "end": end_sec,
            "time": time_str,
        })
    return formatted


# ── Local Whisper Transcription (Fallback) ──────────────────────────────────

def _transcribe_with_local_whisper(
    video_path: Path, model_name: str
) -> dict[str, Any]:
    """Local CPU-based Whisper transcription (slow but offline)."""
    logger.info("Local Whisper transcription started | file=%s | model=%s", video_path.name, model_name)

    try:
        _verify_ffmpeg_available()
        _probe_video_file(video_path)
        whisper = _import_whisper()
        model = whisper.load_model(model_name)
        result = model.transcribe(str(video_path), fp16=False)
    except TranscriptServiceError:
        raise
    except Exception as exc:
        logger.exception("Whisper transcription failed | file=%s", video_path.name)
        raise WhisperTranscriptionError(f"Whisper transcription failed: {exc}") from exc

    transcript_json = _format_segments(result.get("segments", []))
    transcript_text = (result.get("text") or "").strip()

    if not transcript_text:
        raise WhisperTranscriptionError("Whisper returned empty transcript text.")

    logger.info(
        "Local Whisper transcription SUCCESS | file=%s | segments=%s",
        video_path.name,
        len(transcript_json),
    )

    return {
        "transcript_text": transcript_text,
        "transcript_json": transcript_json,
    }


# ── Path Validation ────────────────────────────────────────────────────────

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
        raise UnsupportedVideoFileError(
            f"Unsupported video type. Allowed extensions: {allowed}."
        )

    return resolved_path


# ── FFmpeg Helpers ──────────────────────────────────────────────────────────

def _verify_ffmpeg_available() -> None:
    if shutil.which("ffmpeg") is not None:
        return

    try:
        import imageio_ffmpeg

        ffmpeg_exe = Path(imageio_ffmpeg.get_ffmpeg_exe()).resolve()
        if ffmpeg_exe.exists():
            LOCAL_RUNTIME_FFMPEG_DIR.mkdir(parents=True, exist_ok=True)
            local_ffmpeg = LOCAL_RUNTIME_FFMPEG_DIR / "ffmpeg.exe"
            if (
                not local_ffmpeg.exists()
                or local_ffmpeg.stat().st_size != ffmpeg_exe.stat().st_size
            ):
                shutil.copy2(ffmpeg_exe, local_ffmpeg)

            os.environ["PATH"] = (
                f"{LOCAL_RUNTIME_FFMPEG_DIR}{os.pathsep}{os.environ.get('PATH', '')}"
            )
            if shutil.which("ffmpeg") is not None:
                return
    except Exception:
        logger.debug("imageio-ffmpeg fallback is unavailable.", exc_info=True)

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
            raise UnsupportedVideoFileError(
                "Video file does not contain an audio stream."
            ) from exc
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

        start_sec = round(float(segment.get("start", 0.0)), 2)
        end_sec = round(float(segment.get("end", 0.0)), 2)
        minutes = int(start_sec // 60)
        seconds = int(start_sec % 60)
        time_str = f"{minutes}:{seconds:02d}"

        formatted_segments.append(
            {
                "text": text,
                "start": start_sec,
                "end": end_sec,
                "time": time_str,
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
