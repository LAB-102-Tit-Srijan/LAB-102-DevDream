from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse, ChatResponseData, SummaryResponse, SummaryResponseData
from app.services.auth_service import verify_token
from app.services.chat_service import ask_question, generate_summary

router = APIRouter(
    prefix="/api/videos",
    tags=["Chat"],
)

@router.post("/{video_id}/ask", response_model=ChatResponse)
async def ask_video_question(
    video_id: int, 
    payload: ChatRequest, 
    user: dict = Depends(verify_token)
):
    answer, chunks = ask_question(
        video_id=video_id,
        question=payload.question,
        user_id=user["id"],
        history=payload.history,
    )
    
    # Format sources for response
    sources = []
    for chunk in chunks:
        sources.append({
            "text": chunk.get("chunk_text", ""),
            "start_time": chunk.get("start_time", 0.0),
            "end_time": chunk.get("end_time", 0.0)
        })
    
    return ChatResponse(
        status=True,
        message="Answer generated successfully",
        data=ChatResponseData(
            answer=answer,
            sources=sources,
            video_id=video_id
        )
    )

@router.get("/{video_id}/summary", response_model=SummaryResponse)
async def get_video_summary(
    video_id: int, 
    user: dict = Depends(verify_token)
):
    summary = generate_summary(video_id=video_id, user_id=user["id"])
    
    return SummaryResponse(
        status=True,
        message="Summary generated successfully",
        data=SummaryResponseData(
            summary=summary,
            video_id=video_id
        )
    )
