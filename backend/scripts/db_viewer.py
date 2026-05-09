"""
STUDY AI -- Database Status Viewer
==================================
Run this to see exactly what is inside your Supabase tables.
Usage: python scripts/db_viewer.py
"""

import sys
import os
from pathlib import Path

# Add backend to path so we can import app modules
backend_path = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_path))

from app.db.database import supabase_select

def main():
    print("\n" + "="*60)
    print("  STUDY AI DATABASE STATUS REPORT")
    print("="*60)

    # 1. Check Videos Table
    print("\n[VIDEOS TABLE]")
    try:
        videos = supabase_select("videos")
        if not videos:
            print("  (Empty) No videos uploaded yet.")
        else:
            print(f"{'ID':<4} | {'STATUS':<12} | {'TITLE':<25}")
            print("-" * 50)
            for v in videos:
                print(f"{v.get('id'):<4} | {str(v.get('processing_status')):<12} | {v.get('title')[:25]:<25}")
    except Exception as e:
        print(f"  Error fetching videos: {e}")

    # 2. Check Transcripts Table
    print("\n[TRANSCRIPTS TABLE]")
    try:
        transcripts = supabase_select("transcripts")
        if not transcripts:
            print("  (Empty) No transcripts generated yet.")
        else:
            print(f"{'ID':<4} | {'VID_ID':<6} | {'TEXT PREVIEW'}")
            print("-" * 50)
            for t in transcripts:
                text = t.get('transcript_text', '')[:50].replace('\n', ' ')
                print(f"{t.get('id'):<4} | {t.get('video_id'):<6} | {text}...")
    except Exception as e:
        print(f"  Error fetching transcripts: {e}")

    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    # Ensure scripts directory exists
    os.makedirs("scripts", exist_ok=True)
    main()
