from fastapi import APIRouter, Depends
from ..schemas import GenerateRequest, GenerateResponse
from ..services.ai_service import AIService

router = APIRouter()


def get_ai():
    return AIService()


@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest, ai: AIService = Depends(get_ai)):
    text = await ai.generate(request.prompt, max_tokens=request.max_tokens)
    return GenerateResponse(result=text)
