from fastapi import APIRouter

from src.api.models import ChatRequest, ChatResponse, StandardApiResponse
from src.services.rag.rag_chat import process_user_input

router = APIRouter()


@router.post("/chat", response_model=StandardApiResponse[ChatResponse])
async def chat(request: ChatRequest) -> StandardApiResponse[ChatResponse]:
    """
    Process the user input and return the response.
    """
    user_input = request.user_input
    response_text = await process_user_input(user_input)
    return StandardApiResponse(
        success=True,
        status_code=200,
        message="Chat processed successfully",
        response=ChatResponse(response=response_text),
    )
