"""
interaction_service.py — Service logic for Confused Button, Quiz, and Notes.
ADDITIVE file — does not modify any existing service.
Reuses: retrieval_service.py, embedding_service.py, chat_service.py patterns.
"""

import os
import json
import logging
from typing import List, Dict
from pathlib import Path

import requests
from fastapi import HTTPException

from app.db.database import supabase_select, supabase_insert
from app.services.embedding_service import generate_embeddings
from app.services.retrieval_service import retrieve_relevant_chunks

logger = logging.getLogger(__name__)

# ── AI Provider Config ──────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


def _call_groq(messages: list, temperature: float = 0.4, max_tokens: int = 1024) -> str:
    """Call Groq Llama3 API with structured messages."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not configured")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_gemini(prompt: str) -> str:
    """Fallback to Gemini if Groq fails."""
    import google.generativeai as genai
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-flash-latest",
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=1024,
        )
    )
    response = model.generate_content(prompt)
    return response.text


# ═══════════════════════════════════════════════════════════════════════════
# 1. CONFUSED BUTTON — Simplify / ELI5
# ═══════════════════════════════════════════════════════════════════════════

def simplify_at_timestamp(video_id: int, current_time: float, user_id: str) -> dict:
    """
    Fetches transcript chunks around ±30s of current_time,
    then asks AI to explain it in simple terms (ELI5).
    """
    # Verify ownership
    videos = supabase_select("videos", {"id": f"eq.{video_id}", "uploaded_by": f"eq.{user_id}"})
    if not videos:
        raise HTTPException(status_code=404, detail="Video not found or unauthorized")

    # Ensure embeddings exist
    try:
        generate_embeddings(video_id)
    except Exception as e:
        logger.warning("Embedding generation skipped: %s", e)

    # Strategy: Fetch chunks within ±30s of the current time
    chunk_meta_file = Path("uploads/embeddings") / f"video_{video_id}_chunks.json"
    context_chunks = []

    if chunk_meta_file.exists():
        with open(chunk_meta_file, "r") as f:
            all_chunks = json.load(f)

        lower_bound = max(0, current_time - 30)
        upper_bound = current_time + 30

        for chunk in all_chunks:
            start = chunk.get("start_time", 0)
            end = chunk.get("end_time", 0)
            # Include chunk if it overlaps with the ±30s window
            if start <= upper_bound and end >= lower_bound:
                context_chunks.append(chunk)

    # Fallback: if time-based filtering returns nothing, use semantic search
    if not context_chunks:
        logger.info("Time-based chunk retrieval empty, falling back to semantic search.")
        question = f"What is being discussed around the {int(current_time // 60)}:{int(current_time % 60):02d} minute mark?"
        context_chunks = retrieve_relevant_chunks(video_id, question, top_k=3)

    if not context_chunks:
        # Last resort: grab raw transcript
        transcripts = supabase_select("transcripts", {"video_id": f"eq.{video_id}"})
        if transcripts:
            raw_text = transcripts[0].get("transcript_text", "")
            # Take a slice around the approximate character position
            chars_per_sec = max(1, len(raw_text) / 300)  # rough estimate
            center = int(current_time * chars_per_sec)
            context_text = raw_text[max(0, center - 500):center + 500]
        else:
            context_text = "No transcript available for this video."
    else:
        context_text = "\n".join([c.get("chunk_text", "") for c in context_chunks])

    time_range = f"{max(0, current_time - 30):.0f}s - {current_time + 30:.0f}s"

    prompt = (
        f"You are a friendly tutor. A student is confused at timestamp {current_time:.0f}s of a lecture video.\n\n"
        f"Here is the transcript context around that moment:\n\n"
        f"{context_text}\n\n"
        f"Explain this section in very simple terms. Use analogies. "
        f"Imagine the student is 10 years old. Keep it concise (3-5 sentences max)."
    )

    messages = [
        {"role": "system", "content": "You are a friendly, patient tutor who explains complex topics simply."},
        {"role": "user", "content": prompt}
    ]

    # Try Groq first, fallback to Gemini
    try:
        explanation = _call_groq(messages)
    except Exception as groq_err:
        logger.warning("Groq Simplify Error: %s, falling back to Gemini", groq_err)
        try:
            explanation = _call_gemini(prompt)
        except Exception as gemini_err:
            logger.error("Gemini Simplify Fallback Error: %s", gemini_err)
            raise HTTPException(status_code=500, detail="AI simplification failed. Please try again.")

    return {
        "explanation": explanation,
        "timestamp_range": time_range,
    }


# ═══════════════════════════════════════════════════════════════════════════
# 2. AI QUIZ GENERATION
# ═══════════════════════════════════════════════════════════════════════════

def generate_quiz(video_id: int, user_id: str) -> list:
    """
    Generates 3 MCQ questions from the video transcript.
    Returns a JSON array of quiz questions.
    """
    videos = supabase_select("videos", {"id": f"eq.{video_id}", "uploaded_by": f"eq.{user_id}"})
    if not videos:
        raise HTTPException(status_code=404, detail="Video not found or unauthorized")

    transcripts = supabase_select("transcripts", {"video_id": f"eq.{video_id}"})
    if not transcripts:
        raise HTTPException(status_code=404, detail="Transcript not found. Please wait for transcription to complete.")

    transcript_text = transcripts[0].get("transcript_text", "")
    if not transcript_text:
        raise HTTPException(status_code=404, detail="Transcript is empty.")

    # Truncate for token limits
    truncated = transcript_text[:6000]

    prompt = (
        f"You are a quiz generator for an AI-powered learning platform.\n\n"
        f"Based on the following lecture transcript, generate exactly 3 multiple-choice questions.\n"
        f"Each question should test understanding of key concepts.\n\n"
        f"Transcript:\n{truncated}\n\n"
        f"Return your response as a JSON array with exactly this format (no markdown, no extra text):\n"
        f'[{{"question": "...", "options": ["A", "B", "C", "D"], "correct_index": 0, "timestamp_ref": null}}]\n\n'
        f"Rules:\n"
        f"- Exactly 3 questions\n"
        f"- Exactly 4 options each\n"
        f"- correct_index is 0-based\n"
        f"- Return ONLY the JSON array, nothing else"
    )

    messages = [
        {"role": "system", "content": "You are a JSON-only quiz generator. Return only valid JSON arrays."},
        {"role": "user", "content": prompt}
    ]

    raw_response = ""
    try:
        raw_response = _call_groq(messages, temperature=0.3, max_tokens=1500)
    except Exception as groq_err:
        logger.warning("Groq Quiz Error: %s, falling back to Gemini", groq_err)
        try:
            raw_response = _call_gemini(prompt)
        except Exception as gemini_err:
            logger.error("Gemini Quiz Fallback Error: %s", gemini_err)
            raise HTTPException(status_code=500, detail="Quiz generation failed. Please try again.")

    # Parse AI response — extract JSON from potential markdown wrapper
    try:
        cleaned = raw_response.strip()
        # Strip markdown code fences if present
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)
        
        questions = json.loads(cleaned)

        # Validate structure
        if not isinstance(questions, list):
            raise ValueError("Response is not a JSON array")

        validated = []
        for q in questions[:3]:  # Cap at 3
            validated.append({
                "question": str(q.get("question", "")),
                "options": [str(o) for o in q.get("options", [])[:4]],
                "correct_index": int(q.get("correct_index", 0)),
                "timestamp_ref": q.get("timestamp_ref"),
            })

        return validated

    except (json.JSONDecodeError, ValueError, KeyError) as parse_err:
        logger.error("Failed to parse quiz JSON: %s\nRaw: %s", parse_err, raw_response[:500])
        # Return a graceful fallback instead of crashing
        return [
            {
                "question": "What is the main topic discussed in this lecture?",
                "options": ["Topic A", "Topic B", "Topic C", "Topic D"],
                "correct_index": 0,
                "timestamp_ref": None,
            }
        ]


# ═══════════════════════════════════════════════════════════════════════════
# 3. SMART NOTEPAD — CRUD
# ═══════════════════════════════════════════════════════════════════════════

def get_notes(video_id: int, user_id: str) -> list:
    """Fetch all notes for a user + video, ordered by timestamp."""
    try:
        notes = supabase_select(
            "user_notes",
            {"video_id": f"eq.{video_id}", "user_id": f"eq.{user_id}", "order": "timestamp.asc"}
        )
        return notes or []
    except Exception as e:
        logger.error("Failed to fetch notes: %s", e)
        return []


def create_note(video_id: int, user_id: str, content: str, timestamp: float) -> dict:
    """Insert a new note into user_notes table."""
    payload = {
        "user_id": user_id,
        "video_id": video_id,
        "content": content,
        "timestamp": timestamp,
    }
    try:
        result = supabase_insert("user_notes", payload)
        return result
    except Exception as e:
        logger.error("Failed to create note: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to save note: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════════
# 4. AI-POWERED NOTES GENERATION (Google Docs Ready)
# ═══════════════════════════════════════════════════════════════════════════

def generate_ai_notes(video_id: int, user_id: str) -> dict:
    """
    Generate professional, structured notes from the video transcript.
    Returns formatted text ready for Google Docs or download.
    Structure: Title → Introduction → Key Points → Detailed Notes → Code Snippets → Conclusion
    """
    videos = supabase_select("videos", {"id": f"eq.{video_id}", "uploaded_by": f"eq.{user_id}"})
    if not videos:
        raise HTTPException(status_code=404, detail="Video not found or unauthorized")

    video_title = videos[0].get("title", f"Lecture {video_id}")

    transcripts = supabase_select("transcripts", {"video_id": f"eq.{video_id}"})
    if not transcripts:
        raise HTTPException(status_code=404, detail="Transcript not found. Wait for transcription to complete.")

    transcript_text = transcripts[0].get("transcript_text", "")
    if not transcript_text:
        raise HTTPException(status_code=404, detail="Transcript is empty.")

    # Truncate for token limits (use larger window for notes)
    truncated = transcript_text[:10000]

    prompt = (
        f"You are a professional academic note-taker for an AI-powered learning platform.\n\n"
        f"Based on the following lecture transcript, create comprehensive, well-structured study notes.\n\n"
        f"Lecture Title: {video_title}\n\n"
        f"Transcript:\n{truncated}\n\n"
        f"Generate notes in this exact structure:\n\n"
        f"# {video_title} — Study Notes\n\n"
        f"## 📋 Introduction\n"
        f"(2-3 sentences summarizing the lecture topic and objectives)\n\n"
        f"## 🔑 Key Points\n"
        f"(Bullet list of 5-8 main takeaways)\n\n"
        f"## 📖 Detailed Notes\n"
        f"(Organized by topic/section with clear headings. Include definitions, explanations, and examples.)\n\n"
        f"## 💻 Code Snippets / Formulas\n"
        f"(If any technical content, code, or formulas were discussed, include them here. If none, write 'N/A')\n\n"
        f"## ✅ Conclusion & Key Takeaways\n"
        f"(3-5 sentences wrapping up the main learning outcomes)\n\n"
        f"## 📝 Review Questions\n"
        f"(3 self-test questions to reinforce learning)\n\n"
        f"Rules:\n"
        f"- Write in clear, professional academic language\n"
        f"- Use markdown formatting\n"
        f"- Be thorough but concise\n"
        f"- Include timestamps where relevant (e.g., [02:15])\n"
    )

    messages = [
        {"role": "system", "content": "You are a professional academic note-taker who creates well-structured, comprehensive study materials."},
        {"role": "user", "content": prompt}
    ]

    try:
        notes_text = _call_groq(messages, temperature=0.3, max_tokens=4000)
    except Exception as groq_err:
        logger.warning("Groq AI Notes Error: %s, falling back to Gemini", groq_err)
        try:
            notes_text = _call_gemini(prompt)
        except Exception as gemini_err:
            logger.error("Gemini AI Notes Fallback Error: %s", gemini_err)
            raise HTTPException(status_code=500, detail="AI notes generation failed. Please try again.")

    return {
        "title": f"{video_title} — Study Notes",
        "content": notes_text,
        "video_id": video_id,
    }

