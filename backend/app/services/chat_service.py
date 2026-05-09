import os
from typing import List, Dict
import logging
import google.generativeai as genai
from fastapi import HTTPException
import requests
from app.db.database import supabase_select
from app.services.embedding_service import generate_embeddings
from app.services.retrieval_service import retrieve_relevant_chunks

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"

def _get_gemini_model():
    """Initialize and return configured Gemini model."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured")
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel(
        model_name="gemini-flash-latest",
        generation_config=genai.types.GenerationConfig(
            temperature=0.3,
            max_output_tokens=1024,
        ),
        system_instruction=(
            "You are an AI learning assistant for StudyAI. "
            "You help students understand lecture videos. "
            "Answer questions ONLY using the provided transcript context. "
            "If the answer is not in the context, say: \"I couldn't find that in the video.\""
        )
    )

def _ask_ollama(rag_message: str, history: List[Dict[str, str]]) -> str:
    messages = []
    messages.append({
        "role": "system",
        "content": (
            "You are an AI learning assistant for StudyAI. "
            "You help students understand lecture videos. "
            "Answer questions ONLY using the provided transcript context. "
            "If the answer is not in the context, say: \"I couldn't find that in the video.\""
        )
    })
    
    ALLOWED_ROLES = {"user", "assistant"}
    safe_history = [
        m for m in history[-6:]
        if m.get("role") in ALLOWED_ROLES and m.get("content", "").strip()
    ]
    for msg in safe_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    messages.append({"role": "user", "content": rag_message})
    
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False
    }
    
    response = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=60)
    response.raise_for_status()
    return response.json().get("message", {}).get("content", "")

def _summary_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_GENERATE_URL, json=payload, timeout=60)
    response.raise_for_status()
    return response.json().get("response", "")


def ask_question(video_id: int, question: str, user_id: str, history: List[Dict[str, str]] = []) -> tuple[str, list]:
    # Verify video belongs to user
    videos = supabase_select("videos", {"id": f"eq.{video_id}", "uploaded_by": f"eq.{user_id}"})
    if not videos:
        raise HTTPException(status_code=404, detail="Video not found or unauthorized")

    # Ensure embeddings exist
    try:
        generate_embeddings(video_id)
    except Exception as e:
        logger.error("Embedding generation failed: %s", e)

    # Retrieve relevant chunks via FAISS
    chunks = retrieve_relevant_chunks(video_id, question, top_k=3)

    if chunks:
        context = "\n\n".join([f"[{c['start_time']}s - {c['end_time']}s] {c['chunk_text']}" for c in chunks])
    else:
        # Fallback to full transcript
        logger.warning("Falling back to full transcript due to empty FAISS retrieval")
        transcripts = supabase_select("transcripts", {"video_id": f"eq.{video_id}"})
        if not transcripts:
            raise HTTPException(status_code=404, detail="Transcript not found for this video")
        transcript_text = transcripts[0].get("transcript_text", "")
        if not transcript_text:
            raise HTTPException(status_code=404, detail="Transcript is empty")
        context = transcript_text[:4000]

    rag_message = (
        f"Use the following transcript context to answer my question.\n\n"
        f"Context:\n{context}\n\n"
        f"My Question: {question}"
    )

    try:
        model = _get_gemini_model()

        # Build Gemini chat history from previous turns
        ALLOWED_ROLES = {"user", "assistant"}
        safe_history = [
            m for m in history[-6:]
            if m.get("role") in ALLOWED_ROLES and m.get("content", "").strip()
        ]

        # Convert to Gemini format (uses "user" / "model" roles)
        gemini_history = []
        for msg in safe_history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        # Start chat session with history
        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(rag_message)
        answer = response.text
        return answer, chunks

    except Exception as e:
        logger.warning(f"Gemini Chat Error: {e}, falling back to local Ollama")
        try:
            answer = _ask_ollama(rag_message, history)
            return answer, chunks
        except Exception as ollama_e:
            logger.error(f"Ollama Fallback Error: {ollama_e}")
            raise HTTPException(status_code=500, detail=f"Failed to generate answer via Gemini and Ollama fallback failed: {str(ollama_e)}")


def generate_summary(video_id: int, user_id: str) -> str:
    videos = supabase_select("videos", {"id": f"eq.{video_id}", "uploaded_by": f"eq.{user_id}"})
    if not videos:
        raise HTTPException(status_code=404, detail="Video not found or unauthorized")

    transcripts = supabase_select("transcripts", {"video_id": f"eq.{video_id}"})
    if not transcripts:
        raise HTTPException(status_code=404, detail="Transcript not found for this video")

    transcript_text = transcripts[0].get("transcript_text", "")
    if not transcript_text:
        raise HTTPException(status_code=404, detail="Transcript is empty")

    # Return cached summary if it exists
    existing_summary = videos[0].get("summary")
    if existing_summary:
        return existing_summary

    prompt = (
        f"You are an AI learning assistant. Write a concise, bulleted summary of the following "
        f"lecture transcript. Highlight the main concepts and key takeaways.\n\n"
        f"Transcript:\n{transcript_text[:6000]}\n\nSummary:"
    )

    summary_text = ""
    try:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured")
            
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=1024,
            )
        )
        response = model.generate_content(prompt)
        summary_text = response.text

    except Exception as e:
        logger.warning(f"Gemini Summary Error: {e}, falling back to local Ollama")
        try:
            summary_text = _summary_ollama(prompt)
        except Exception as ollama_e:
            logger.error(f"Ollama Fallback Error: {ollama_e}")
            raise HTTPException(status_code=500, detail=f"Failed to generate summary via Gemini and Ollama fallback failed: {str(ollama_e)}")

    # Save summary back to video record (optional — graceful fail)
    try:
        from app.db.database import supabase_client
        supabase_client.table("videos").update({"summary": summary_text}).eq("id", video_id).execute()
    except Exception as update_err:
        logger.warning(f"Could not save summary to DB (missing column?): {update_err}")

    return summary_text
