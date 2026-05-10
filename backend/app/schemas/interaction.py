"""
Pydantic schemas for Confused Button, Smart Notepad, and AI Quizzes.
These are ADDITIVE — no existing schemas are touched.
"""

from pydantic import BaseModel
from typing import List, Optional


# ── Confused / Simplify ────────────────────────────────────────────────────

class SimplifyRequest(BaseModel):
    current_time: float  # seconds into the video


class SimplifyResponseData(BaseModel):
    explanation: str
    timestamp_range: str  # e.g. "120s - 180s"


class SimplifyResponse(BaseModel):
    status: bool
    message: str
    data: SimplifyResponseData


# ── AI Quiz ────────────────────────────────────────────────────────────────

class QuizOption(BaseModel):
    text: str


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_index: int
    timestamp_ref: Optional[float] = None


class QuizResponseData(BaseModel):
    questions: List[QuizQuestion]
    video_id: int


class QuizResponse(BaseModel):
    status: bool
    message: str
    data: QuizResponseData


# ── Smart Notepad ──────────────────────────────────────────────────────────

class NoteCreate(BaseModel):
    content: str
    timestamp: float = 0.0


class NoteOut(BaseModel):
    id: int
    user_id: str
    video_id: int
    content: str
    timestamp: float
    created_at: str


class NotesListResponse(BaseModel):
    status: bool
    message: str
    data: List[NoteOut]


class NoteCreateResponse(BaseModel):
    status: bool
    message: str
    data: NoteOut


# ── Google Docs Integration ────────────────────────────────────────────────

class GoogleDocsCreateRequest(BaseModel):
    title: str
    content: str


class GoogleDocsResponseData(BaseModel):
    doc_id: str
    doc_url: str
    title: str


class GoogleDocsResponse(BaseModel):
    status: bool
    message: str
    data: GoogleDocsResponseData


class GoogleDocsAppendRequest(BaseModel):
    doc_id: str
    content: str


class GoogleAuthStatusResponse(BaseModel):
    status: bool
    connected: bool
    auth_url: Optional[str] = None


# ── AI Notes Generation ───────────────────────────────────────────────────

class AINotesResponseData(BaseModel):
    title: str
    content: str
    video_id: int
    doc_url: Optional[str] = None


class AINotesResponse(BaseModel):
    status: bool
    message: str
    data: AINotesResponseData

