import logging
from typing import Optional
from app.db.database import supabase_select

logger = logging.getLogger(__name__)

MAX_WORDS = 400

def _safe_float(value, default: float = 0.0) -> float:
    """Safely coerce a timestamp to float. Returns default if None or invalid."""
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def create_chunks(video_id: int):
    """
    Step 4A: Split transcript_json into logical chunks.
    Rules: 300-500 words max, preserve timestamps and continuity.
    """
    # 1. Fetch transcript from DB
    transcripts = supabase_select("transcripts", {"video_id": f"eq.{video_id}"})
    if not transcripts:
        raise ValueError("Transcript not found")

    transcript_json = transcripts[0].get("transcript_json")
    if not transcript_json or not isinstance(transcript_json, list):
        raise ValueError("Transcript is empty or malformed")

    # Filter out non-dict and empty segments before processing
    valid_segments = [
        s for s in transcript_json
        if isinstance(s, dict) and s.get("text", "").strip()
    ]
    if not valid_segments:
        raise ValueError("Transcript contains no valid text segments")

    chunks = []
    current_chunk_text = []
    current_word_count = 0
    start_time: Optional[float] = None
    end_time: float = 0.0
    chunk_index = 1

    for segment in valid_segments:
        text = segment["text"].strip()
        words = text.split()

        if not current_chunk_text:
            start_time = _safe_float(segment.get("start"), default=0.0)

        current_chunk_text.append(text)
        current_word_count += len(words)
        end_time = _safe_float(segment.get("end"), default=start_time or 0.0)

        # When chunk reaches max words, flush it
        if current_word_count >= MAX_WORDS:
            chunks.append({
                "chunk_text": " ".join(current_chunk_text),
                "start_time": start_time,
                "end_time": end_time,
                "video_id": video_id,
                "chunk_index": chunk_index
            })
            chunk_index += 1
            current_chunk_text = []
            current_word_count = 0
            start_time = None

    # Flush remaining text as the last chunk
    if current_chunk_text:
        chunks.append({
            "chunk_text": " ".join(current_chunk_text),
            "start_time": start_time if start_time is not None else 0.0,
            "end_time": end_time,
            "video_id": video_id,
            "chunk_index": chunk_index
        })

    logger.info("Created %s chunks for video_id=%s", len(chunks), video_id)
    return chunks
