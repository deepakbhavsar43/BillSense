from fastapi import APIRouter, HTTPException

from app.schemas.genai import ChatRequest, ChatResponse, GenerateRequest, GenerateResponse
from app.services.genai_service import genai_service

router = APIRouter()


async def _run_chat(payload: ChatRequest) -> ChatResponse:
    try:
        output_text = await genai_service.generate(
            prompt=payload.prompt,
            system_prompt=payload.system_prompt,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
        )
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ChatResponse(text=output_text, provider=genai_service.provider)


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    return await _run_chat(payload)


@router.post("/generate", response_model=GenerateResponse)
async def generate_text(payload: GenerateRequest) -> GenerateResponse:
    response = await _run_chat(payload)
    return GenerateResponse(text=response.text, provider=response.provider)
