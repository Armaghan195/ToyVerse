from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, ChatHistoryResponse
from app.services.chatbot_service import ChatbotService
from app.models.user import User
from app.api.dependencies import (
    get_chatbot_service,
    get_current_user,
    get_optional_user,
)

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

@router.post("/message", response_model=dict)
async def send_message(
    request: ChatMessageRequest,
    chatbot_service: ChatbotService = Depends(get_chatbot_service),
    current_user: Optional[User] = Depends(get_optional_user)
):
    try:
        result = chatbot_service.process_message(
            message=request.message,
            session_id=request.session_id,
            user_id=current_user.id if current_user else None
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )

@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_conversation_history(
    session_id: str,
    limit: int = Query(50, ge=1, le=100),
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    messages = chatbot_service.get_conversation_history(session_id, limit)

    return ChatHistoryResponse(
        session_id=session_id,
        messages=[
            ChatMessageResponse(
                id=msg.id,
                message=msg.message,
                response=msg.response,
                session_id=msg.session_id,
                user_id=msg.user_id,
                created_at=msg.created_at
            )
            for msg in messages
        ],
        total_messages=len(messages)
    )

@router.delete("/history/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def clear_conversation(
    session_id: str,
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    success = chatbot_service.clear_conversation(session_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to clear conversation history"
        )

@router.get("/user-history", response_model=list[ChatMessageResponse])
async def get_user_chat_history(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    messages = chatbot_service._repository.get_by_user(current_user.id, skip=0, limit=limit)

    return [
        ChatMessageResponse(
            id=msg.id,
            message=msg.message,
            response=msg.response,
            session_id=msg.session_id,
            user_id=msg.user_id,
            created_at=msg.created_at
        )
        for msg in messages
    ]
