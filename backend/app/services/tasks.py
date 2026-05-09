import logging
import traceback
import time
from pathlib import Path
from app.services.transcript_service import generate_transcript
from app.services.transcript_storage_service import save_transcript, DuplicateTranscriptError
from app.db.database import supabase_update, supabase_select

logger = logging.getLogger(__name__)


def process_video_transcript_background(video_id: int, file_path: str):
    """
    Background task to generate and save transcript after upload.
    Uses Groq API (fast) with local Whisper fallback.
    """
    logger.info(f"[BG-TASK] Starting transcription | video_id={video_id} | file_path={file_path}")
    start_time = time.time()

    try:
        # Check if transcript already exists (duplicate upload protection)
        existing = supabase_select("transcripts", {"video_id": f"eq.{video_id}"})
        if existing:
            logger.info(f"[BG-TASK] Transcript already exists | video_id={video_id} | skipping")
            supabase_update("videos", {"id": f"eq.{video_id}"}, {"processing_status": "transcribed"})
            return

        # Resolve path
        backend_root = Path(__file__).resolve().parent.parent.parent
        video_path = backend_root / file_path
        
        logger.info(f"[BG-TASK] Resolved video path: {video_path}")
        logger.info(f"[BG-TASK] File exists: {video_path.exists()}")

        if not video_path.exists():
            logger.error(f"[BG-TASK] FAILED: File not found at {video_path}")
            supabase_update("videos", {"id": f"eq.{video_id}"}, {"processing_status": "failed"})
            return
            
        # 0. Update status to transcribing immediately
        logger.info(f"[BG-TASK] Setting status to 'transcribing' | video_id={video_id}")
        supabase_update("videos", {"id": f"eq.{video_id}"}, {"processing_status": "transcribing"})

        # 1. Generate Transcript (Groq API first, then Whisper fallback)
        logger.info(f"[BG-TASK] Starting transcript generation | video_id={video_id}")
        transcript_data = generate_transcript(video_path, model_name="tiny")
        
        gen_time = round(time.time() - start_time, 1)
        logger.info(f"[BG-TASK] Transcript generated in {gen_time}s | video_id={video_id} | segments={len(transcript_data.get('transcript_json', []))}")

        # 2. Save to DB
        logger.info(f"[BG-TASK] Saving transcript to DB | video_id={video_id}")
        save_transcript(
            video_id=video_id,
            transcript_text=transcript_data["transcript_text"],
            transcript_json=transcript_data["transcript_json"]
        )
        
        total_time = round(time.time() - start_time, 1)
        logger.info(f"[BG-TASK] SUCCESS | video_id={video_id} | total_time={total_time}s")

    except DuplicateTranscriptError:
        logger.info(f"[BG-TASK] Duplicate transcript detected | video_id={video_id} | marking as transcribed")
        try:
            supabase_update("videos", {"id": f"eq.{video_id}"}, {"processing_status": "transcribed"})
        except Exception:
            pass

    except Exception as e:
        elapsed = round(time.time() - start_time, 1)
        logger.error(f"[BG-TASK] FAILED | video_id={video_id} | elapsed={elapsed}s | error={e}")
        logger.error(f"[BG-TASK] Full traceback:\n{traceback.format_exc()}")
        try:
            supabase_update("videos", {"id": f"eq.{video_id}"}, {"processing_status": "failed"})
        except Exception:
            pass
