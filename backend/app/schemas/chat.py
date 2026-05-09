from pydantic import BaseModel
from typing import List, Dict

class ChatRequest(BaseModel):
    question: str
    history: List[Dict[str, str]] = []  # Optional — [{role: "user"/"assistant", content: "..."}]

class ChatSource(BaseModel):
    text: str
    start_time: float
    end_time: float

class ChatResponseData(BaseModel):
    answer: str
    sources: list[ChatSource]
    video_id: int

class ChatResponse(BaseModel):
    status: bool
    message: str
    data: ChatResponseData

class SummaryResponseData(BaseModel):
    summary: str
    video_id: int

class SummaryResponse(BaseModel):
    status: bool
    message: str
    data: SummaryResponseData
