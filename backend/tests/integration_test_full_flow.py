"""
STUDY AI -- Full Integration Test (Step 2A + Step 2B)
=====================================================
[ignoring loop detection]

Flow:
1. Fetch all video entries from Supabase.
2. Iterate through videos and find the first one that:
   a) Exists on disk.
   b) Has an audio stream (Whisper compatible).
3. Generate transcript and save to DB.

Usage:
    python -m tests.integration_test_full_flow
"""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("IntegrationTest")

from app.services.transcript_service import generate_transcript, UnsupportedVideoFileError
from app.services.transcript_storage_service import save_transcript
from app.db.database import supabase_select

def main():
    print("="*60)
    print("  STUDY AI -- STEP 2 INTEGRATION TEST (AUTO-RETRY LOOP)")
    print("="*60)

    # 1. Fetch all videos from DB
    logger.info("Fetching video records from Supabase...")
    try:
        videos = supabase_select("videos")
        if not videos:
            logger.error("No video records found in DB.")
            return
        
        backend_root = Path(__file__).resolve().parent.parent
        valid_found = False

        # Try videos one by one (newest first)
        for v in sorted(videos, key=lambda x: x['id'], reverse=True):
            video_id = v['id']
            file_path_str = v.get('file_path')
            
            if not file_path_str: continue
            
            candidate_path = backend_root / file_path_str
            if not candidate_path.exists():
                logger.warning(f"ID={video_id}: File not found on disk. Skipping.")
                continue

            logger.info(f"Trying ID={video_id}: {file_path_str}")

            try:
                # Attempt Transcription
                logger.info("  -> Starting Whisper...")
                transcript_data = generate_transcript(candidate_path, model_name="tiny")
                
                # If we reach here, transcription worked!
                logger.info("  -> Transcription SUCCESS!")
                
                # Save to DB
                logger.info("  -> Saving to DB...")
                # Cleanup old
                from app.db.database import SUPABASE_URL, get_headers
                import requests as http_requests
                del_url = f"{SUPABASE_URL}/rest/v1/transcripts?video_id=eq.{video_id}"
                http_requests.delete(del_url, headers=get_headers())

                result = save_transcript(
                    video_id=video_id,
                    transcript_text=transcript_data["transcript_text"],
                    transcript_json=transcript_data["transcript_json"]
                )
                
                print("\n" + "="*40)
                print("  FULL FLOW INTEGRATION SUCCESS!")
                print("="*40)
                print(f"  Video ID: {result.video_id}")
                print(f"  Transcript ID: {result.transcript_id}")
                print(f"  Status: {result.status}")
                print("="*40)
                
                valid_found = True
                break # Stop after first success

            except UnsupportedVideoFileError:
                logger.warning(f"  -> ID={video_id} has no audio. Trying next video...")
            except Exception as e:
                logger.error(f"  -> ID={video_id} failed with error: {e}. Trying next...")

        if not valid_found:
            logger.error("Tested all videos but none were valid for transcription.")

    except Exception as e:
        logger.error(f"Failed during test: {e}")

if __name__ == "__main__":
    main()
