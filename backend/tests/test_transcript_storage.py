"""
STEP 2B -- Transcript Storage Functional Test
=============================================

Run from backend/ directory with venv activated:
    python -m tests.test_transcript_storage

Tests:
    1. Valid save -- real video_id, proper transcript data
    2. Invalid video_id -- should fail with VideoNotFoundError
    3. Empty transcript -- should fail with Pydantic ValidationError
    4. Duplicate save -- should fail with DuplicateTranscriptError
    5. Malformed JSON -- should fail with Pydantic ValidationError
    6. Timestamp verification -- stored timestamps match input exactly
"""

import json
import logging
import sys

# Configure logging so we see service logs during testing
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)

from app.services.transcript_storage_service import (
    save_transcript,
    DuplicateTranscriptError,
    TranscriptInsertError,
    TranscriptStorageError,
    VideoNotFoundError,
)
from app.db.database import supabase_select
from pydantic import ValidationError


# -- Test Data ---------------------------------------------------------------

SAMPLE_TRANSCRIPT_TEXT = (
    "Today we will learn about recursion. "
    "Recursion is when a function calls itself. "
    "Let us look at a simple example using factorial."
)

SAMPLE_TRANSCRIPT_JSON = [
    {"text": "Today we will learn about recursion.", "start": 0.0, "end": 4.5},
    {"text": "Recursion is when a function calls itself.", "start": 4.5, "end": 9.2},
    {"text": "Let us look at a simple example using factorial.", "start": 9.2, "end": 14.8},
]

PASSED = 0
FAILED = 0


def report(test_name: str, passed: bool, detail: str = ""):
    global PASSED, FAILED
    if passed:
        PASSED += 1
        print(f"  [PASS] {test_name}")
    else:
        FAILED += 1
        print(f"  [FAIL] {test_name} -- {detail}")


# -- Helpers -----------------------------------------------------------------

def get_real_video_id() -> int | None:
    """Fetch a real video_id from the videos table for testing."""
    try:
        rows = supabase_select("videos")
        if rows:
            return rows[0]["id"]
    except Exception:
        pass
    return None


def cleanup_test_transcript(video_id: int) -> None:
    """Delete test transcript to allow re-running tests."""
    from app.db.database import SUPABASE_URL, get_headers
    import requests as http_requests

    url = f"{SUPABASE_URL}/rest/v1/transcripts?video_id=eq.{video_id}"
    headers = get_headers()
    try:
        http_requests.delete(url, headers=headers)
    except Exception:
        pass


# -- Tests -------------------------------------------------------------------

def test_1_valid_save(video_id: int):
    """Test: Save a valid transcript for a real video_id."""
    print("\n-- TEST 1: Valid Transcript Save --")

    # Cleanup any previous test data
    cleanup_test_transcript(video_id)

    try:
        result = save_transcript(
            video_id=video_id,
            transcript_text=SAMPLE_TRANSCRIPT_TEXT,
            transcript_json=SAMPLE_TRANSCRIPT_JSON,
        )
        report("save_transcript returned result", True)
        report(f"transcript_id = {result.transcript_id}", result.transcript_id > 0)
        report(f"video_id = {result.video_id}", result.video_id == video_id)
        report(f"segments_count = {result.segments_count}", result.segments_count == 3)
        report(f"status = {result.status}", result.status == "success")
        return True
    except Exception as exc:
        report("save_transcript execution", False, str(exc))
        return False


def test_2_invalid_video_id():
    """Test: Saving with a non-existent video_id should fail."""
    print("\n-- TEST 2: Invalid video_id --")
    try:
        save_transcript(
            video_id=999999,
            transcript_text=SAMPLE_TRANSCRIPT_TEXT,
            transcript_json=SAMPLE_TRANSCRIPT_JSON,
        )
        report("Should have raised VideoNotFoundError", False, "No exception raised")
    except VideoNotFoundError as exc:
        report(f"VideoNotFoundError raised correctly: {exc}", True)
    except Exception as exc:
        report("Wrong exception type", False, f"{type(exc).__name__}: {exc}")


def test_3_empty_transcript():
    """Test: Empty transcript_text should fail Pydantic validation."""
    print("\n-- TEST 3: Empty transcript --")
    try:
        save_transcript(
            video_id=1,
            transcript_text="",
            transcript_json=SAMPLE_TRANSCRIPT_JSON,
        )
        report("Should have raised ValidationError", False, "No exception raised")
    except ValidationError as exc:
        report("ValidationError raised correctly", True)
    except Exception as exc:
        report("Wrong exception type", False, f"{type(exc).__name__}: {exc}")


def test_4_duplicate_save(video_id: int):
    """Test: Saving a second transcript for the same video should fail."""
    print("\n-- TEST 4: Duplicate transcript --")
    try:
        save_transcript(
            video_id=video_id,
            transcript_text=SAMPLE_TRANSCRIPT_TEXT,
            transcript_json=SAMPLE_TRANSCRIPT_JSON,
        )
        report("Should have raised DuplicateTranscriptError", False, "No exception raised")
    except DuplicateTranscriptError as exc:
        report(f"DuplicateTranscriptError raised correctly: {exc}", True)
    except Exception as exc:
        report("Wrong exception type", False, f"{type(exc).__name__}: {exc}")


def test_5_malformed_json():
    """Test: Malformed transcript_json should fail validation."""
    print("\n-- TEST 5: Malformed transcript_json --")

    # Missing required 'end' field
    bad_json = [{"text": "hello", "start": 0.0}]
    try:
        save_transcript(
            video_id=1,
            transcript_text="hello",
            transcript_json=bad_json,
        )
        report("Should have raised ValidationError", False, "No exception raised")
    except ValidationError as exc:
        report("ValidationError raised for missing 'end' field", True)
    except Exception as exc:
        report("Wrong exception type", False, f"{type(exc).__name__}: {exc}")

    # Negative start time
    bad_json_2 = [{"text": "hello", "start": -5.0, "end": 2.0}]
    try:
        save_transcript(
            video_id=1,
            transcript_text="hello",
            transcript_json=bad_json_2,
        )
        report("Should have raised ValidationError", False, "No exception raised")
    except ValidationError as exc:
        report("ValidationError raised for negative start time", True)
    except Exception as exc:
        report("Wrong exception type", False, f"{type(exc).__name__}: {exc}")

    # end < start
    bad_json_3 = [{"text": "hello", "start": 10.0, "end": 5.0}]
    try:
        save_transcript(
            video_id=1,
            transcript_text="hello",
            transcript_json=bad_json_3,
        )
        report("Should have raised ValidationError", False, "No exception raised")
    except ValidationError as exc:
        report("ValidationError raised for end < start", True)
    except Exception as exc:
        report("Wrong exception type", False, f"{type(exc).__name__}: {exc}")


def test_6_timestamp_verification(video_id: int):
    """Test: Verify that stored timestamps match input exactly."""
    print("\n-- TEST 6: Timestamp Verification --")
    try:
        rows = supabase_select("transcripts", {"video_id": f"eq.{video_id}"})
        if not rows:
            report("Transcript found in DB", False, "No rows returned")
            return

        stored = rows[0]
        stored_json = stored.get("transcript_json", [])

        report("Transcript row found in DB", True)
        report(
            f"Segment count matches ({len(stored_json)} == {len(SAMPLE_TRANSCRIPT_JSON)})",
            len(stored_json) == len(SAMPLE_TRANSCRIPT_JSON),
        )

        all_timestamps_match = True
        for i, (stored_seg, input_seg) in enumerate(
            zip(stored_json, SAMPLE_TRANSCRIPT_JSON)
        ):
            if (
                stored_seg["start"] != input_seg["start"]
                or stored_seg["end"] != input_seg["end"]
                or stored_seg["text"] != input_seg["text"]
            ):
                all_timestamps_match = False
                report(
                    f"Segment {i} match",
                    False,
                    f"stored={stored_seg} vs input={input_seg}",
                )

        if all_timestamps_match:
            report("All timestamps preserved exactly", True)

        # Verify transcript_text
        report(
            "transcript_text matches",
            stored.get("transcript_text") == SAMPLE_TRANSCRIPT_TEXT,
        )

    except Exception as exc:
        report("Timestamp verification", False, str(exc))


# -- Main --------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  STEP 2B -- Transcript Storage Functional Tests")
    print("=" * 60)

    # Get a real video_id from the database
    video_id = get_real_video_id()
    if not video_id:
        print("\n[ABORT] No videos found in the database.")
        print("   Upload a video first using the frontend or API.")
        sys.exit(1)

    print(f"\nUsing video_id = {video_id} for testing\n")

    # Run tests in order
    save_ok = test_1_valid_save(video_id)
    test_2_invalid_video_id()
    test_3_empty_transcript()

    if save_ok:
        test_4_duplicate_save(video_id)
        test_6_timestamp_verification(video_id)
    else:
        print("\n[WARNING] Skipping tests 4 and 6 (test 1 failed)")

    test_5_malformed_json()

    # Summary
    print("\n" + "=" * 60)
    print(f"  RESULTS: {PASSED} passed, {FAILED} failed")
    print("=" * 60)

    if FAILED > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
